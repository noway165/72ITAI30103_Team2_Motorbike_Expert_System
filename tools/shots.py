"""Screenshots of every MotoLogic diagnosis screen, for checking the layout by eye.

    python tools/shots.py                      # vi + en, light + dark, default + minimum window
    python tools/shots.py --lang=vi --mode=light --size=default --out=C:/temp/shots

The window must stay visible on screen while the script runs (PIL.ImageGrab copies the screen).
Images go to a temporary folder (printed at the end), never into git.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import tkinter as tk  # noqa: E402

from PIL import ImageGrab  # noqa: E402

import gui  # noqa: E402
import gui_widgets as w  # noqa: E402
import theme  # noqa: E402
from gui_diagnosis import new_dx  # noqa: E402

PICK = ("starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years")
CHAT = {"vi": ["đề chỉ nghe tạch tạch", "tại sao hỏi vậy?", "có", "còn khả năng nào?"],
        "en": ["the starter only clicks", "why?", "yes", "what else?"]}
TALK = {"vi": "Sáng nay đề chỉ nghe tạch tạch, còi cũng yếu, ắc quy dùng hơn 2 năm rồi",
        "en": "The starter only clicks, the horn is weak and the battery is over 2 years old"}


def arg(name: str, default: str) -> str:
    for a in sys.argv[1:]:
        if a.startswith(f"--{name}="):
            return a.split("=", 1)[1]
    return default


def grab(root: tk.Tk, path: Path) -> None:
    for _ in range(3):  # autowrap labels re-layout after the first <Configure>
        root.update()
    root.after(250)
    root.update()
    x, y = root.winfo_rootx(), root.winfo_rooty()
    ImageGrab.grab((x, y, x + root.winfo_width(), y + root.winfo_height()), all_screens=True).save(path)
    print(path.name)


def page(app):
    return app.pages["diagnosis"]


def reset(app, **kw):
    app.state["dx"] = dict(new_dx(), **kw)
    app.state["history"] = []
    app.show("diagnosis")
    p = page(app)
    p.dx = app.state["dx"]
    p.render()
    return p


def screens(root: tk.Tk, app, out: Path, tag: str) -> None:
    def shot(name):
        grab(root, out / f"{tag}_{name}.png")

    reset(app)
    shot("1_setup")
    p = reset(app, method="guided")
    p.start()
    shot("2a_part_card")
    p.change_part("starting_fuel")
    shot("2a_guided_first")
    for v in (True, False, True):
        if p.dx["step"] == 2:
            p.answer_guided(v)
    shot("2a_guided_3answers")
    p = reset(app, method="symptoms")
    p.start()
    shot("2b_symptoms_empty")
    for sid in PICK:
        p.toggle_symptom(sid)
    shot("2b_symptoms_selected")
    p = reset(app, method="talk")
    p.start()
    shot("2c_talk_empty")
    p.text.insert("1.0", CHAT[app.lang][0])
    p.analyze()
    shot("2c_chat_start")
    for msg in CHAT[app.lang][1:]:
        p.send(msg)
    shot("2c_chat_why_answer")
    p = reset(app, method="talk")
    p.start()
    p.dx.update(text="xyz abc", replies=[])
    p.render()
    shot("2c_talk_not_understood")
    p = reset(app, method="symptoms")
    p.start()
    for sid in PICK:
        p.toggle_symptom(sid)
    p.finish()
    shot("3_result")
    rec = app.state["history"][p.dx["record"]]
    p.verify(rec, rec.result.diagnoses[0].fault)
    shot("3_result_verified")


def main() -> int:
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError, ImportError):
        pass
    langs = [arg("lang", "")] if arg("lang", "") else ["vi", "en"]
    modes = [arg("mode", "")] if arg("mode", "") else ["light", "dark"]
    sizes = [arg("size", "")] if arg("size", "") else ["default", "min"]
    out = Path(arg("out", tempfile.mkdtemp(prefix="motologic_shots_")))
    out.mkdir(parents=True, exist_ok=True)
    root = tk.Tk()
    root.attributes("-topmost", True)
    app = gui.App(root, langs[0])
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()  # same size rule as gui.App
    default = f"{min(w.px(theme.WINDOW_SIZE[0]), int(sw * 0.94))}x{min(w.px(theme.WINDOW_SIZE[1]), int(sh * 0.88))}"
    minimum = f"{w.px(theme.WINDOW_MIN_SIZE[0])}x{w.px(theme.WINDOW_MIN_SIZE[1])}"
    for lang in langs:
        app.set_lang(lang)
        for mode in modes:
            app.set_mode(mode)
            for size in sizes:
                root.geometry((default if size == "default" else minimum) + "+0+0")
                root.update()
                screens(root, app, out, f"{lang}_{mode}_{size}")
    app.set_mode("light")
    root.destroy()
    print(f"\n{out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
