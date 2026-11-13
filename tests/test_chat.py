"""Tests for chat.py: the rule-based conversation of "Describe it in words" (owner: Lâm)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from chat import intent, parse_answer, respond, start  # noqa: E402
from gui_diagnosis import new_dx, talk_interview  # noqa: E402
from kb import load_kb  # noqa: E402

KB = load_kb()
SE01 = "Sáng nay xe Vision đề chỉ nghe tạch tạch, còi cũng yếu"


def chat(text="", lang="vi"):
    dx = new_dx()
    dx.update(method="talk", step=2, kind="scooter", fuel="fi")
    if text:
        start(KB, dx, text, lang)
    return dx


def pending(dx):
    q = talk_interview(KB, dx)[0].next_question()
    return q.symptom if q else None


class ParseTest(unittest.TestCase):
    def test_answers(self):
        for text, want in (("có", True), ("Ừ đúng rồi", True), ("chắc vậy", True), ("yes", True),
                           ("không", False), ("ko", False), ("chưa", False), ("no", False),
                           ("không rõ", None), ("không biết", None), ("not sure", None)):
            with self.subTest(text=text):
                self.assertEqual(parse_answer(text), (True, want))

    def test_a_description_is_not_an_answer(self):
        for text in ("không nổ", "còi yếu", "no power uphill"):
            with self.subTest(text=text):
                self.assertFalse(parse_answer(text)[0])

    def test_intents(self):
        for text, want in (("tại sao hỏi vậy?", "why"), ("why?", "why"), ("làm sao biết vậy", "how"),
                           ("sửa thế nào", "fix"), ("what should I do", "fix"), ("còn khả năng nào khác", "others"),
                           ("cầu chì tổng là gì", "what"), ("làm lại", "restart"), ("xem kết quả", "result"),
                           ("còi cũng yếu", None),
                           # asked by a user on 13/11
                           ("có cách nào tốt hơn không", "better"), ("có cách khác không", "better"),
                           ("có cách nào sửa không", "fix"), ("phải làm sao giờ", "fix"),
                           ("có nguy hiểm không", "fix"), ("is there a better way", "better"),
                           ("can I still ride it", "fix"), ("đèn có sáng không", None)):
            with self.subTest(text=text):
                self.assertEqual(intent(text), want)


class ConversationTest(unittest.TestCase):
    def test_start_says_what_was_read_and_asks_a_question_from_the_kb(self):
        dx = chat(SE01)
        bot = "\n".join(t for who, t in dx["chat"] if who == "bot")
        self.assertIn(KB.text("horn_weak", "vi").rstrip(" ?"), bot)
        q = pending(dx)
        self.assertIsNotNone(q)
        self.assertIn(KB.question(q, "vi"), bot)

    def test_answer_is_recorded_and_the_rule_effect_reported(self):
        dx = chat(SE01)
        q = pending(dx)
        out = respond(KB, dx, "có", "vi")
        self.assertEqual(dx["replies"][-1], (q, True))
        self.assertTrue(out)

    def test_why_quotes_the_rules_that_use_the_question(self):
        dx = chat(SE01)
        q = pending(dx)
        out = "\n".join(respond(KB, dx, "tại sao hỏi câu này?", "vi"))
        self.assertTrue(any(r.id in out for r in KB.rules_using(q)), out)
        self.assertEqual(dx["replies"], [])  # still waiting for the answer
        self.assertEqual(pending(dx), q)

    def test_why_differs_with_the_question(self):
        a, b = chat(SE01), chat("Phanh trước kêu rít")
        wa = respond(KB, a, "tại sao", "vi")
        wb = respond(KB, b, "tại sao", "vi")
        self.assertNotEqual(wa, wb)

    def test_more_symptoms_mid_conversation(self):
        dx = chat("đề chỉ nghe tạch tạch")
        respond(KB, dx, "à còi cũng yếu", "vi")
        found = {m.symptom for m in talk_interview(KB, dx)[1]}
        self.assertIn("horn_weak", found)

    def test_answer_and_more_symptoms_in_one_message(self):
        dx = chat(SE01)
        q = pending(dx)
        respond(KB, dx, "có, mà đèn pha cũng không sáng", "vi")
        self.assertEqual(dx["replies"][0], (q, True))
        self.assertIn("headlight_off", {m.symptom for m in talk_interview(KB, dx)[1]})

    def test_fix_and_how_come_from_the_leading_fault(self):
        dx = chat(SE01 + ", ắc quy dùng hơn 2 năm rồi")
        iv, _ = talk_interview(KB, dx)
        top = iv.result().diagnoses[0].fault
        fix = "\n".join(respond(KB, dx, "sửa thế nào?", "vi"))
        self.assertIn(KB.action(top, "vi"), fix)
        how = "\n".join(respond(KB, dx, "làm sao biết?", "vi"))
        self.assertTrue(any(r.id in how for r in KB.rules_concluding(top)), how)

    def test_fix_gives_the_specs_of_the_bike_named_in_the_text(self):
        dx = chat("Vision sáng nay đề chỉ nghe tạch tạch, còi cũng yếu, ắc quy dùng hơn 2 năm rồi")
        fix = "\n".join(respond(KB, dx, "sửa thế nào?", "vi"))
        self.assertIn("GTZ6V", fix)  # Honda Vision battery, from its owner's manual

    def test_others_lists_the_beliefs(self):
        dx = chat(SE01)
        out = "\n".join(respond(KB, dx, "còn khả năng nào?", "vi"))
        for fault, _ in talk_interview(KB, dx)[0].beliefs(3):
            self.assertIn(KB.text(fault, "vi"), out)

    def test_what_is_a_fault(self):
        dx = chat(SE01)
        out = "\n".join(respond(KB, dx, "đứt cầu chì tổng là gì?", "vi"))
        self.assertIn(KB.action("blown_main_fuse", "vi"), out)
        self.assertTrue(any(r.id in out for r in KB.rules_concluding("blown_main_fuse")))

    def test_what_with_part_of_a_name_prefers_a_fault(self):
        out = respond(KB, chat(SE01), "ắc quy là gì?", "vi")[0]
        self.assertIn(KB.text("weak_battery", "vi"), out)

    def test_no_zero_percent_faults_listed(self):
        bot = "\n".join(t for who, t in chat(SE01)["chat"] if who == "bot")
        self.assertNotIn("(0%)", bot)

    def test_not_understood_keeps_everything(self):
        dx = chat(SE01)
        q, text = pending(dx), dx["text"]
        out = respond(KB, dx, "xyz abc", "vi")
        self.assertTrue(out)
        self.assertEqual((pending(dx), dx["text"], dx["replies"]), (q, text, []))

    def test_restart(self):
        dx = chat(SE01)
        respond(KB, dx, "có", "vi")
        respond(KB, dx, "làm lại", "vi")
        self.assertEqual((dx["text"], dx["replies"]), ("", []))

    def test_conversation_reaches_a_proved_fault_with_wang(self):
        dx = chat(SE01)
        truth = {"starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years", "is_scooter",
                 "is_fuel_injected"}
        for _ in range(20):
            q = pending(dx)
            if q is None:
                break
            respond(KB, dx, "có" if q in truth else "không", "vi")
        last = dx["chat"][-1][1]
        self.assertIn(KB.text("weak_battery", "vi"), last)
        self.assertIn("Wang", last)

    def test_english(self):
        dx = chat("The starter only clicks and the horn is weak", "en")
        q = pending(dx)
        out = "\n".join(respond(KB, dx, "why?", "en"))
        self.assertTrue(any(r.id in out for r in KB.rules_using(q)))
        self.assertIn(KB.question(q, "en"), "\n".join(t for _, t in dx["chat"]))


if __name__ == "__main__":
    unittest.main()
