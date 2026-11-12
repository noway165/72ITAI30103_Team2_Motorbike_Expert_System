"""Extra measurements for Chapter 4 and 5 (owner: Khoa; tasks K4 and K6 of 12/11).

    python tools/compare_fair.py            # fair comparison: backward chaining against the assistant
    python tools/compare_fair.py --noise    # 10% and 20% of the answers flipped (about 12 minutes)

Fair comparison: the assistant reads the description and stops early, backward chaining does neither.
So backward chaining is also run (a) started from the same description and (b) stopping at the first
fault it proves. Bike-model questions are not counted (the model is chosen in step 1).
Results are written up in docs/progress/nguyen_nam_khoa.md, sections 3 and 6.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import evaluate_assistant as ea  # noqa: E402
from backward_chaining import BackwardSession  # noqa: E402
from interview import MAX_QUESTIONS, Interview, simulate  # noqa: E402
from kb import load_kb  # noqa: E402
from nlu import answers  # noqa: E402
from scenarios import load_scenarios  # noqa: E402

kb = load_kb()


def bw(truth, start):
    s=BackwardSession(kb, None, answers=dict(start)); n0=len(s.answers)
    while not s.finished: s.answer(s.question.symptom in truth)
    return sum(1 for k in list(s.answers)[n0:] if k not in kb.models), s.result
def first_proof(truth):
    ans={}; asked=0
    for g in sorted(kb.faults):
        s=BackwardSession(kb,[g],answers=ans)
        while not s.finished: q=s.question.symptom; s.answer(q in truth); asked+= q not in kb.models
        ans=dict(s.answers)
        if s.result.diagnoses: return asked,g
    return asked,None
def table(name, scs, langs=("vi","en"), plain=True):
    print("##",name,len(scs))
    if plain:
        q=[]; ok=0
        for sc in scs:
            n,r=bw(set(sc.symptoms),{}); q.append(n); ok+= bool(r.diagnoses) and r.diagnoses[0].fault==sc.expected
        print(f"backward all parts          {sum(q)/len(q):5.1f}  {ok}/{len(scs)}")
        q=[];ok=0
        for sc in scs:
            n,g=first_proof(set(sc.symptoms)); q.append(n); ok+= g==sc.expected
        print(f"backward first proof        {sum(q)/len(q):5.1f}  {ok}/{len(scs)}")
    for lang in langs:
        qb=[];okb=0;qa=[];oka=0;cap=[];miss=[]
        for sc in scs:
            st=answers(sc.description[lang], kb.symptoms)
            n,r=bw(set(sc.symptoms),st); qb.append(n); okb+= bool(r.diagnoses) and r.diagnoses[0].fault==sc.expected
            iv,a=simulate(kb,sc.symptoms,st); qa.append(a); good=[d.fault for d in iv.result().diagnoses][:1]==[sc.expected]; oka+=good
            if a>=MAX_QUESTIONS: cap.append(sc.id)
            if not good: miss.append((sc.id,sc.expected))
        print(f"backward + {lang} description   {sum(qb)/len(qb):5.1f}  {okb}/{len(scs)}")
        print(f"assistant {lang}                {sum(qa)/len(qa):5.1f}  {oka}/{len(scs)}  capped {len(cap)} {cap}  misses {miss}")


VEH={"is_scooter","is_manual","is_fuel_injected","is_carburetor","has_clutch_lever"} | set(kb.models)
def noisy(truth, p, rng, memo):
    def ans(sym):
        if sym not in memo:
            v = sym in truth
            memo[sym] = (not v) if (sym not in VEH and rng.random() < p) else v
        return memo[sym]
    return ans
def run_bw(sc, p, seed, part):
    rng=random.Random(seed); a=noisy(set(sc.symptoms),p,rng,{})
    goals=sorted(f for f,s in kb.faults.items() if s.subsystem==kb.symbols[sc.expected].subsystem) if part else None
    s=BackwardSession(kb,goals)
    while not s.finished: s.answer(a(s.question.symptom))
    d=s.result.diagnoses; return bool(d) and d[0].fault==sc.expected, s.result.questions_asked
def run_as(sc, p, seed, lang):
    rng=random.Random(seed); a=noisy(set(sc.symptoms),p,rng,{})
    iv=Interview(kb, answers(sc.description[lang], kb.symptoms) if lang else None)
    while (q:=iv.next_question()) is not None: iv.answer(q.symptom, a(q.symptom))
    d=[x.fault for x in iv.result().diagnoses][:1]; return d==[sc.expected], len(iv.asked)


def fair():
    table("30 scenarios", load_scenarios())
    table("held-out", [s for s in load_scenarios(ea.HELD_OUT_DIR) if s.id.startswith("HO")])


def noise(seeds=20):
    scs = load_scenarios()
    print("flipped | backward, all parts | backward, right part | assistant, vi text | assistant, no text")
    for p in (0.0, 0.1, 0.2):
        row = []
        for f, arg in ((run_bw, False), (run_bw, True), (run_as, "vi"), (run_as, None)):
            ok = q = n = 0
            for i, sc in enumerate(scs):
                for sd in range(seeds):
                    o, qq = f(sc, p, sd * 1000 + i, arg)
                    ok += o
                    q += qq
                    n += 1
            row.append(f"{100 * ok / n:5.1f}% {q / n:5.1f}q")
        print(f"{p:.0%} | " + " | ".join(row))


if __name__ == "__main__":
    noise() if "--noise" in sys.argv else fair()
