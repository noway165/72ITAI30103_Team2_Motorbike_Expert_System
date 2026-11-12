"""Text on the "Hỏi đáp từng câu" screen stays readable in light and dark mode.

Contrast ratio as defined by WCAG 2.1: at least 4.5:1 for normal text. Every pair
below is a (text colour, background colour) that src/gui_backward.py and the
widgets it uses actually draw. When a colour in src/theme.py changes, run this
test before opening the Pull Request.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import theme  # noqa: E402

# (text, background, where it is drawn on the screen)
PAIRS = [
    ("text", "surface", "question, results"),
    ("muted", "surface", "hint, answered list, fault counts"),
    ("accent", "surface", "links \"Tại sao hỏi câu này?\", open count"),
    ("accent_hover", "surface", "link under the mouse"),
    ("on_accent", "accent", "Bắt đầu / Hỏi lại, rank badge 1"),
    ("on_accent", "accent_hover", "primary button under the mouse"),
    ("on_accent", "ok", "Có button"),
    ("on_accent", "ok_hover", "Có button under the mouse"),
    ("on_accent", "danger", "Không button"),
    ("on_accent", "danger_hover", "Không button under the mouse"),
    ("ok", "surface", "answered \"Có\""),
    ("danger", "surface", "answered \"Không\""),
    ("text", "accent_soft", "why / how box"),
    ("muted", "accent_soft", "CF in the why / how box"),
    ("accent", "accent_soft", "rank badge 2 to 5"),
    ("muted", "chrome", "status bar with the keys"),
    ("warn", "warn_soft", "\"Không biết\" notice, no fault reached"),
    ("text", "warn_soft", "near misses"),
    ("muted", "warn_soft", "CF of near misses"),
    ("ok", "ok_soft", "chip \"Tự xử lý được\""),
    ("danger", "danger_soft", "chip \"Cần mang ra thợ\""),
    ("text", "bg", "page title"),
    ("muted", "bg", "page subtitle"),
]

MIN_RATIO = 4.5


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


class ContrastTest(unittest.TestCase):
    def test_formula(self):
        self.assertAlmostEqual(contrast("#000000", "#FFFFFF"), 21.0, places=2)
        self.assertAlmostEqual(contrast("#777777", "#777777"), 1.0, places=6)

    def test_backward_screen_is_readable_in_both_modes(self):
        for name, palette in (("light", theme.LIGHT), ("dark", theme.DARK)):
            for fg, bg, where in PAIRS:
                with self.subTest(mode=name, fg=fg, bg=bg, where=where):
                    ratio = contrast(palette[fg], palette[bg])
                    self.assertGreaterEqual(ratio, MIN_RATIO,
                                            f"{name}: {fg} on {bg} ({where}) is {ratio:.2f}:1")

    def test_hover_keys_exist_in_both_modes(self):
        for key in ("ok_hover", "danger_hover", "accent_hover"):
            self.assertIn(key, theme.LIGHT)
            self.assertIn(key, theme.DARK)


if __name__ == "__main__":
    unittest.main()
