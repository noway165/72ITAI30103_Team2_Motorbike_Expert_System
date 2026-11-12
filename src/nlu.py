"""Understanding a rider's own words (owner: Lâm).

Turns a free description in Vietnamese or English, such as
    "Sáng nay đề chỉ nghe tạch tạch, còi cũng yếu, bình dùng 3 năm rồi"
    "The starter just clicks and the horn is weak"
into symptom answers of the knowledge base: {"starter_clicks_or_silent": True, ...}.

Method: every symptom has a list of short phrases (Vietnamese, including
Southern words such as "thắng" for brake, and English). Text and phrases are
compared without accents, word by word. A negation word just before a phrase
("không", "chưa", "no", "not", ...) turns the answer into False.
No internet and no model files are needed, so it also runs inside the .exe.

    from nlu import extract
    for m in extract("còi yếu, không có khói đen"):
        print(m.symptom, m.value, m.start, m.end)
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

# Phrases per symptom. Write them naturally; they are folded (no accents, lower case) when loaded.
PHRASES: Dict[str, List[str]] = {
    # --- vehicle type -------------------------------------------------------
    "is_scooter": ["xe tay ga", "tay ga", "xe ga", "vision", "air blade", "airblade", "lead", "sh mode", "sh",
                   "pcx", "vario", "nvx", "grande", "janus", "attila", "vespa", "liberty", "click",
                   "scooter", "automatic"],
    "is_manual": ["xe số", "xe so", "wave", "dream", "future", "sirius", "jupiter", "exciter", "winner",
                  "raider", "satria", "cub", "manual", "geared", "gear bike"],
    "is_fuel_injected": ["phun xăng", "phun xăng điện tử", "fi", "fuel injection", "fuel injected", "injection",
                         "vision", "air blade", "airblade", "lead", "sh", "pcx", "vario", "nvx", "grande", "janus",
                         "winner", "exciter"],
    "is_carburetor": ["bình xăng con", "chế hòa khí", "carburetor", "carburettor", "carb", "dream"],
    "has_clutch_lever": ["côn tay", "tay côn", "có côn", "clutch lever", "exciter", "winner", "raider", "satria"],
    # --- starting and fuel --------------------------------------------------
    "starter_clicks_or_silent": ["tạch tạch", "tạch", "lạch cạch khi đề", "đề không quay", "đề không lên",
                                 "đề im re", "đề không ăn", "bấm đề im", "đề không có tiếng", "không có phản ứng", "only clicks",
                                 "just clicks", "nothing happens",
                                 "starter clicks", "starter does nothing", "nothing happens when i press start",
                                 "starter is silent"],
    "engine_cranks": ["máy vẫn quay", "máy có quay", "đề máy quay", "đề vẫn quay", "đạp máy quay",
                      "cranks", "turns over", "engine turns"],
    "engine_wont_start": ["không nổ", "không chịu nổ", "không nổ máy", "khó nổ", "nổ không được",
                          "won t start", "wont start", "does not start", "doesn t start", "will not start",
                          "no start", "not starting"],
    "horn_weak": ["còi yếu", "còi kêu yếu", "kèn yếu", "còi rè", "còi nhỏ", "weak horn", "horn is weak",
                  "horn weak", "horn sounds weak"],
    "horn_normal": ["còi kêu to", "còi vẫn kêu to", "còi bình thường", "còi vẫn to", "kèn kêu to",
                    "horn is loud", "horn works", "horn sounds normal", "loud horn"],
    "horn_silent": ["còi không kêu", "còi im", "mất còi", "kèn không kêu", "horn does not work",
                    "horn doesn t work", "no horn", "horn is dead", "horn silent"],
    "dash_lights_off_key_on": ["đồng hồ không sáng", "đèn đồng hồ tắt", "mất điện", "không có điện",
                               "đồng hồ tắt ngúm", "đồng hồ tối", "tối om", "dashboard dark", "dash lights off", "no power",
                               "dashboard does not light", "dashboard is dead"],
    "battery_older_than_2_years": ["bình dùng 3 năm", "bình 3 năm", "ắc quy cũ", "bình cũ", "bình lâu rồi",
                                   "ắc quy 3 năm", "ắc quy 4 năm", "bình 4 năm", "bình 2 năm", "ắc quy 2 năm",
                                   "old battery", "battery is old", "battery is 3 years", "years old battery"],
    "battery_recently_replaced": ["mới thay bình", "mới thay ắc quy", "bình mới thay", "ắc quy mới thay",
                                  "new battery", "battery was replaced", "replaced the battery"],
    "bike_unused_over_2_weeks": ["để lâu không chạy", "để lâu", "lâu không chạy", "bỏ xe lâu", "để cả tháng",
                                 "đi du lịch về", "not ridden for weeks", "unused for weeks", "left it for weeks",
                                 "sat for a month", "has not been used"],
    "starting_without_brake": ["quên bóp phanh", "không bóp phanh", "quên bóp thắng", "không bóp thắng",
                               "without the brake", "forgot the brake", "without pulling the brake",
                               "didn t hold the brake"],
    "brake_held_when_starting": ["đã bóp phanh", "có bóp phanh", "vừa bóp phanh vừa đề", "đã bóp thắng",
                                 "có bóp thắng", "holding the brake", "held the brake", "pulled the brake"],
    "fuel_gauge_empty": ["hết xăng", "kim xăng chỉ e", "xăng cạn", "cạn xăng", "kim xăng e", "gauge shows e", "out of fuel",
                         "out of petrol", "out of gas", "fuel gauge on e", "tank is empty", "empty tank"],
    "fuel_level_ok": ["còn xăng", "xăng còn", "vẫn còn xăng", "đầy xăng", "mới đổ xăng", "đầy bình",
                      "has fuel", "there is fuel", "fuel in the tank", "plenty of fuel", "tank is full", "still has petrol", "full tank"],
    "strong_fuel_smell": ["mùi xăng", "nồng mùi xăng", "ngửi thấy xăng", "smell of petrol", "smells of petrol",
                          "smell of gas", "fuel smell", "petrol smell", "gasoline smell"],
    "no_fuel_pump_hum_key_on": ["không nghe bơm xăng", "không nghe tiếng bơm", "bơm xăng không kêu",
                                "bơm xăng im", "không nghe rè rè", "no fuel pump hum", "fuel pump is silent",
                                "can t hear the fuel pump", "no pump noise"],
    "side_stand_down": ["chân chống nghiêng", "quên gạt chân chống", "chống nghiêng hạ", "chưa gạt chống",
                        "side stand down", "kickstand down", "side stand is down"],
    # --- ignition and electrics --------------------------------------------
    "engine_misfires": ["nổ không đều", "giật cục", "lúc nổ lúc tắt", "nổ lụp bụp", "máy ho", "nổ ì ạch",
                        "misfire", "misfires", "stutters", "sputters", "runs rough", "cuts out"],
    "spark_plug_overdue": ["lâu chưa thay bugi", "bugi cũ", "chưa thay bugi", "bugi lâu rồi", "bugi chưa từng thay", "plug has never been replaced",
                           "spark plug is old", "old spark plug", "never changed the spark plug"],
    "battery_goes_flat_repeatedly": ["hay hết bình", "bình hay hết điện", "hết điện hoài", "sạc rồi vẫn hết",
                                     "hết bình liên tục", "vẫn hay hết điện", "battery keeps dying", "keeps going flat",
                                     "battery dies again"],
    "headlight_off": ["đèn pha không sáng", "mất đèn pha", "đèn trước không sáng", "đèn pha tắt", "cháy đèn",
                      "headlight not working", "headlight is out", "no headlight", "headlight off"],
    "other_lights_work": ["xi nhan vẫn sáng", "đèn hậu vẫn sáng", "các đèn khác vẫn sáng", "đèn khác bình thường",
                          "other lights work", "indicators work", "tail light works", "tail light work"],
    "electrics_cut_out_over_bumps": ["qua ổ gà thì tắt", "qua chỗ xóc thì tắt", "chập chờn khi xóc",
                                     "đi đường xóc là tắt", "cuts out over bumps", "flickers over bumps",
                                     "dies over bumps"],
    # --- engine -------------------------------------------------------------
    "black_exhaust_smoke": ["khói đen", "ra khói đen", "black smoke"],
    "blue_white_exhaust_smoke": ["khói trắng", "khói xanh", "khói xám", "khói mùi nhớt", "ăn nhớt",
                                 "blue smoke", "white smoke", "grey smoke", "burning oil"],
    "fuel_consumption_increased": ["hao xăng", "tốn xăng", "ăn xăng", "tốn hơn", "fuel use", "uses more fuel", "fuel consumption",
                                   "burns more fuel", "drinking fuel", "poor mileage"],
    "engine_lacks_power": ["máy yếu", "yếu máy", "đuối", "lên dốc yếu", "không bốc", "thiếu lực", "ì máy",
                           "lacks power", "no power uphill", "weak engine", "sluggish"],
    "air_filter_overdue": ["lâu chưa thay lọc gió", "lọc gió bẩn", "chưa thay lọc gió", "lọc gió cũ", "lọc gió chưa thay",
                           "dirty air filter", "air filter is old", "air filter has not been changed", "never changed the air filter"],
    "oil_level_low": ["nhớt cạn", "thiếu nhớt", "nhớt dưới vạch", "nhớt thấp", "low oil", "oil is low",
                      "oil level low"],
    "engine_ticking_noise": ["máy kêu lạch cạch", "tiếng gõ", "máy gõ", "kêu lách cách trong máy",
                             "ticking", "knocking", "tapping noise"],
    "oil_change_overdue": ["lâu chưa thay nhớt", "quá hạn thay nhớt", "chưa thay nhớt", "trễ thay nhớt",
                           "oil change overdue", "past its oil change", "overdue for an oil change", "haven t changed the oil"],
    "oil_dark_or_thick": ["nhớt đen", "nhớt đặc", "que thăm đen", "black and thick", "nhớt có cặn", "dark oil", "black oil", "thick oil",
                          "sludgy oil"],
    "oil_drops_between_changes": ["hao nhớt", "nhớt hụt nhanh", "hụt nhớt", "mất nhớt", "uses oil", "oil level drops",
                                  "losing oil", "oil disappears"],
    "temp_warning_light_on": ["đèn nhiệt độ", "đèn báo nhiệt", "báo nóng máy", "nóng máy", "quá nhiệt",
                              "temperature light", "overheating", "temp light", "engine overheats"],
    "coolant_below_min": ["thiếu nước làm mát", "nước làm mát cạn", "nước mát dưới vạch", "hết nước mát",
                          "low coolant", "coolant is low", "coolant below"],
    "radiator_fan_not_running": ["quạt không quay", "quạt két nước không chạy", "không nghe quạt", "không nghe tiếng quạt", "fan cannot be heard",
                                 "fan not running", "fan doesn t run", "radiator fan does not work"],
    "engine_stalls_at_idle": ["chết máy", "tắt máy khi dừng", "hay tắt máy", "tắt máy ở đèn đỏ", "ga nhỏ tắt",
                              "stalls", "stalls at idle", "dies at idle", "dies at the lights"],
    # --- transmission -------------------------------------------------------
    "revs_rise_but_slow": ["rú ga mà chậm", "máy gào mà chậm", "máy rú nhưng", "without the bike speeding up", "revs hard but", "rú mà không đi", "ga lên mà xe không đi",
                           "trượt côn", "trượt nồi", "revs but slow", "revs high but slow", "slipping",
                           "engine revs but"],
    "cvt_belt_overdue": ["chưa thay dây curoa", "dây curoa cũ", "curoa lâu rồi", "dây đai cũ",
                         "belt is old", "belt never replaced", "dây curoa chưa thay", "chưa thay dây curoa", "never changed the belt", "drive belt overdue"],
    "rattle_from_cvt_cover": ["lạch xạch ở nồi", "kêu ở nồi", "vỏ nồi kêu", "lục cục bên trái",
                              "rattle from the cvt", "rattling from the left cover", "cvt rattle"],
    "judder_when_pulling_away": ["rung giật khi chạy", "giật khi mới chạy", "khựng khi ra ga", "rung đầu",
                                 "judder", "judders", "shudders when pulling away"],
    "clicking_noise_from_rear": ["tiếng ở nhông sên", "nhông sên dĩa kêu", "xích kêu", "sên kêu", "lách cách ở xích", "clicking from the chain",
                                 "chain noise", "noise from the chain", "clicking from the rear"],
    "chain_slack_high": ["xích chùng", "sên chùng", "sên trùng", "xích lỏng", "sên lỏng", "loose chain",
                         "chain is loose", "chain slack"],
    "chain_dry_or_rusty": ["xích khô", "sên khô", "xích gỉ", "sên gỉ", "xích rỉ sét", "rusty chain",
                           "dry chain", "chain is dry"],
    "hard_to_shift_gears": ["khó vào số", "sang số nặng", "vào số cứng", "hard to shift", "gears are hard",
                            "difficult to change gear"],
    "clutch_free_play_out_of_spec": ["tay côn rơ", "côn rơ", "côn bị rơ", "clutch free play",
                                     "clutch lever is loose"],
    # --- brakes -------------------------------------------------------------
    "brake_squeal": ["phanh kêu rít", "thắng kêu rít", "phanh kêu két", "thắng kêu", "phanh kêu",
                     "brakes squeal", "brake squeal", "squeaky brakes", "brakes squeak"],
    "brake_grinding": ["phanh kêu ken két", "kêu sắt cọ sắt", "phanh kêu rè rè sắt", "brakes grind",
                       "grinding brakes", "metal on metal"],
    "brake_pad_thin_visible": ["má phanh mỏng", "bố thắng mỏng", "mòn bố", "hết bố", "má phanh mòn",
                               "worn brake pads", "brake pads are thin", "thin pads"],
    "brake_stopping_distance_longer": ["phanh không ăn", "thắng không ăn", "phanh ăn kém", "thắng yếu",
                                       "phanh yếu", "brakes are weak", "takes longer to stop",
                                       "brakes don t bite"],
    "brake_lever_spongy": ["tay phanh mềm", "tay thắng mềm", "bóp phanh sâu", "phanh bị lún",
                           "spongy brake", "soft brake lever", "spongy lever", "lever feels spongy", "lever feels soft"],
    "brake_fluid_low": ["dầu phanh cạn", "dầu thắng cạn", "thiếu dầu phanh", "dầu phanh dưới vạch",
                        "low brake fluid", "brake fluid is low"],
    "brake_fluid_leak_visible": ["rỉ dầu phanh", "chảy dầu phanh", "rỉ dầu thắng", "dầu phanh rỉ",
                                 "brake fluid leak", "leaking brake fluid"],
    "brake_fluid_old": ["lâu chưa thay dầu phanh", "dầu phanh cũ", "chưa thay dầu thắng", "old brake fluid",
                        "brake fluid is old"],
    "brake_pulsation": ["phanh bị rung", "thắng bị rung", "bóp phanh rung", "phanh giật",
                        "brake pulsation", "brakes pulse", "vibration when braking"],
    "brake_drags": ["bó phanh", "bó thắng", "phanh bị bó", "bánh nặng", "phanh bị kéo", "brakes drag",
                    "brake drags", "wheel feels heavy"],
    # --- tyres and suspension ----------------------------------------------
    "tyre_pressure_low": ["lốp non", "vỏ non", "non hơi", "lốp xẹp", "lốp bẹp", "flat tyre", "flat tire",
                          "low tyre pressure", "low tire pressure", "tyre is soft"],
    "tyre_loses_air_quickly": ["xì hơi", "hay xì", "bơm hoài", "mau xẹp", "loses air", "tyre keeps going flat", "tire keeps going flat",
                               "slow puncture"],
    "tyre_foreign_object": ["dính đinh", "cán đinh", "đinh trong lốp", "đinh trên vỏ", "nail in the tyre",
                            "nail in the tire", "screw in the tyre"],
    "tyre_wear_uneven": ["lốp mòn lệch", "mòn không đều", "vỏ mòn lệch", "uneven tyre wear",
                         "uneven tire wear", "cupped tyre"],
    "vehicle_pulls_to_one_side": ["xe bị kéo lệch", "xe bị lệch", "tay lái lệch", "pulls to one side",
                                  "pulls to the left", "pulls to the right"],
    "steering_heavy": ["tay lái nặng", "khó bẻ lái", "heavy steering", "steering is heavy"],
    "fork_oil_on_tube": ["phuộc trước rỉ dầu", "chảy dầu phuộc", "phuộc chảy dầu", "fork leaking oil",
                         "oil on the fork"],
    "front_suspension_soft": ["phuộc trước mềm", "chúi đầu", "phuộc yếu", "soft front suspension",
                              "front dives", "front forks are soft"],
    "rear_shock_bouncy": ["giảm xóc sau nảy", "phuộc sau nảy", "xe bị nhún", "nhún nhiều", "nảy nhiều",
                          "bouncy rear", "rear bounces", "bouncy shock"],
    "rear_shock_oil_leak": ["phuộc sau chảy dầu", "giảm xóc sau rỉ dầu", "rear shock leaking",
                            "oil on the rear shock"],
    "sits_low_parked": ["xe đứng thấp", "xe bị lún", "đuôi xe thấp", "sits low", "rear sags", "sagging"],
    "suspension_clunk": ["lộc cộc ở phuộc", "phuộc kêu", "giảm xóc kêu", "kêu lộc cộc", "clunk",
                         "clunking", "suspension knocks"],
}

NEGATORS = {"khong", "chua", "ko", "k", "hong", "kh", "no", "not", "never", "without", "isn", "doesn", "didn",
            "wasn", "don"}
FILLERS = {"bi", "co", "thay", "nghe", "con", "phai", "he", "the", "is", "have", "has", "any", "see", "hear",
           "smell", "a"}

# A specific symptom found in the text removes a more general one it contradicts.
EXCLUDES = {
    "starter_clicks_or_silent": {"engine_cranks", "engine_wont_start"},
    "brake_grinding": {"brake_squeal"},
    "horn_silent": {"horn_weak", "horn_normal"},
    "horn_weak": {"horn_normal"},
}


def fold(text: str) -> str:
    """Lower case without accents, one output character per input character (keeps offsets)."""
    out = []
    for ch in text:
        base = unicodedata.normalize("NFD", ch)[:1] or ch
        out.append("d" if ch in "đĐ" else base.lower()[:1] or ch)
    return "".join(out)


MAX_GAP = 2  # words allowed between the words of a phrase: "còi cũng yếu", "horn is very weak"


def _tokens(folded: str) -> List[Tuple[str, int, int, int]]:
    """(word, start, end, clause number); a new clause starts after , . ; ! ? and similar."""
    out, clause = [], 0
    for m in re.finditer(r"[a-z0-9]+|[,.;:!?()\n]", folded):
        if m.group()[0].isalnum():
            out.append((m.group(), m.start(), m.end(), clause))
        else:
            clause += 1
    return out


def _find(words, clauses, phrase, start):
    """Index of the last word of `phrase` matched from `start`, allowing small gaps, or -1."""
    j = start
    for k, w in enumerate(phrase):
        if k == 0:
            if words[j] != w:
                return -1
            continue
        for step in range(1, MAX_GAP + 2):
            if j + step < len(words) and clauses[j + step] == clauses[start] and words[j + step] == w:
                j += step
                break
        else:
            return -1
    return j


_PHRASE_TOKENS = {sid: [fold(p).replace("'", " ").split() for p in ps] for sid, ps in PHRASES.items()}


@dataclass
class Match:
    symptom: str
    value: bool        # False when the phrase is negated ("không có khói đen")
    phrase: str        # the words that matched, as written by the rider
    start: int         # character offsets in the original text
    end: int


def extract(text: str, known: Iterable[str] = ()) -> List[Match]:
    """Symptoms mentioned in `text`, one Match per symptom (the first mention wins).

    `known` restricts the result to symptoms of the knowledge base.
    """
    allowed = set(known) or set(PHRASES)
    folded = fold(text)
    toks = _tokens(folded)
    words = [t[0] for t in toks]
    clauses = [t[3] for t in toks]
    found: Dict[str, Match] = {}
    for sid, variants in _PHRASE_TOKENS.items():
        if sid not in allowed:
            continue
        for phrase in sorted(variants, key=len, reverse=True):  # longest phrase first
            for i in range(len(words)):
                j = _find(words, clauses, phrase, i)
                if j < 0:
                    continue
                prev1 = words[i - 1] if i >= 1 and clauses[i - 1] == clauses[i] else ""
                prev2 = words[i - 2] if i >= 2 and clauses[i - 2] == clauses[i] else ""
                negated = prev1 in NEGATORS or (prev2 in NEGATORS and prev1 in FILLERS)
                m = Match(sid, not negated, text[toks[i][1]:toks[j][2]], toks[i][1], toks[j][2])
                old = found.get(sid)
                if old is None or (m.value and not old.value):
                    found[sid] = m
                break
    ms = sorted(found.values(), key=lambda m: m.end - m.start, reverse=True)
    for i, a in enumerate(ms):
        for b in ms[i + 1:]:
            if b.symptom in found and a.symptom in found and a.start < b.end and b.start < a.end \
                    and (b.end - b.start) < (a.end - a.start) and a.phrase.lower() != b.phrase.lower():
                del found[b.symptom]
    for sid, removes in EXCLUDES.items():
        if sid in found and found[sid].value:
            for r in removes:
                if r in found and found[r].value:
                    del found[r]
    return sorted(found.values(), key=lambda m: m.start)


def answers(text: str, known: Iterable[str] = ()) -> Dict[str, bool]:
    """{symptom: True/False} read from the rider's text."""
    return {m.symptom: m.value for m in extract(text, known)}
