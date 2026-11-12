"""Shared look of the program (owner: Lâm). Every UI part imports from here.

The visual guide (screens, colours, wording) is docs/ui_guide.md.
Do not type colour codes or font names anywhere else: use these names, and if a
new colour is needed, add it here through a Pull Request.

    import tkinter as tk
    import theme
    root = tk.Tk()
    theme.apply(root)
    tk.Label(root, text="Lỗi", fg=theme.COLORS["text"], font=theme.FONTS["heading"])

For charts (evaluation script):
    import theme
    theme.apply_matplotlib()
    plt.bar(x, y, color=theme.ENGINE_COLORS["forward"])
"""

from __future__ import annotations

COLORS = {
    "accent": "#0E5E6F",        # title bar, primary button, CF bar, result #1
    "accent_hover": "#0A4A58",  # primary button when hovered / pressed
    "accent_soft": "#DCECEF",   # "why" box, selected item
    "bg": "#E9EEF0",            # window background
    "surface": "#FFFFFF",       # panels, result cards, entries
    "chrome": "#DAE3E6",        # status bar, CF bar trough, disabled button
    "border": "#C8D3D7",        # 1 px border of panels, cards, entries
    "text": "#132228",
    "muted": "#5B6B70",         # hints, counts, status bar text
    "on_accent": "#FFFFFF",     # text on accent / ok / danger
    "ok": "#2E7D4F",            # severity "self", Yes button, Wang agrees
    "ok_soft": "#E3F1E8",
    "danger": "#B3261E",        # severity "mechanic", No button, errors
    "danger_soft": "#F8E1DF",
    "warn": "#8A5A00",          # not enough evidence for any fault
    "warn_soft": "#FBEFD6",
    "sidebar": "#082E37",       # left navigation
    "sidebar_hover": "#0E3E49",
    "sidebar_active": "#11505D",
    "sidebar_text": "#D5E6EA",
    "sidebar_muted": "#8FB1B9",
    "highlight": "#E9A23B",     # selected nav item, title underline, home screen accents
    "highlight_soft": "#FCEFD9",
    "hero": "#0A4652",          # dark end of the home screen banner
}

# One colour per subsystem: group dots in the GUI and charts by subsystem.
SUBSYSTEM_COLORS = {
    "starting_fuel": "#0E5E6F",
    "ignition_electrical": "#C98A0B",
    "engine": "#B5561D",
    "transmission": "#4A5BA8",
    "brakes": "#7A4C9A",
    "tyres_suspension": "#5F6B3A",
}

# One colour per inference method in every chart and slide.
ENGINE_COLORS = {
    "forward": COLORS["accent"],
    "backward": "#C98A0B",
    "wang": "#4A5BA8",
}

SUBSYSTEM_NAMES = {
    "vi": {
        "vehicle": "Loại xe",
        "starting_fuel": "Khởi động, nhiên liệu",
        "ignition_electrical": "Đánh lửa, điện",
        "engine": "Động cơ",
        "transmission": "Truyền động",
        "brakes": "Phanh",
        "tyres_suspension": "Lốp, giảm xóc",
    },
    "en": {
        "vehicle": "Vehicle type",
        "starting_fuel": "Starting and fuel",
        "ignition_electrical": "Ignition and electrics",
        "engine": "Engine",
        "transmission": "Transmission",
        "brakes": "Brakes",
        "tyres_suspension": "Tyres and suspension",
    },
}

SUBSYSTEM_ORDER = ["starting_fuel", "ignition_electrical", "engine",
                   "transmission", "brakes", "tyres_suspension"]

UI_FONT = "Segoe UI"   # installed on every Windows machine
MONO_FONT = "Consolas"

FONTS = {
    "display": (UI_FONT, 22, "bold"),   # page titles, big numbers on tiles
    "title": (UI_FONT, 12, "bold"),     # program name, card titles
    "question": (UI_FONT, 13, "bold"),  # question in step-by-step mode
    "heading": (UI_FONT, 10, "bold"),   # panel titles, fault names, buttons
    "body": (UI_FONT, 10),
    "small": (UI_FONT, 9),              # hints, counts, status bar, why/how
    "small_bold": (UI_FONT, 9, "bold"),  # severity chips, step labels
    "mono": (MONO_FONT, 9),             # rule ids, CF values
    "mono_bold": (MONO_FONT, 9, "bold"),
}

PAD = {"xs": 4, "s": 8, "m": 12, "l": 16}

WINDOW_SIZE = (1200, 760)
WINDOW_MIN_SIZE = (1040, 660)
SIDEBAR_WIDTH = 216
LEFT_COLUMN_WIDTH = 360
MAX_RESULTS = 5

# Wording shown to the rider (see docs/ui_guide.md, "Cách gọi tên").
SEVERITY_TEXT = {
    "vi": {"self": "Tự xử lý được", "mechanic": "Cần mang ra thợ"},
    "en": {"self": "You can fix it", "mechanic": "Take it to a mechanic"},
}


def severity_colors(severity: str | None):
    """(foreground, background) of the severity chip."""
    if severity == "mechanic":
        return COLORS["danger"], COLORS["danger_soft"]
    return COLORS["ok"], COLORS["ok_soft"]


LIGHT = dict(COLORS)
DARK = {
    "accent": "#2E9AAD", "accent_hover": "#45B2C5", "accent_soft": "#163A42",
    "bg": "#0F191C", "surface": "#172428", "chrome": "#22343A", "border": "#2E464D",
    "text": "#E3EEF0", "muted": "#93A9AF", "on_accent": "#FFFFFF",
    "ok": "#4CB57F", "ok_soft": "#173A28", "danger": "#E5675E", "danger_soft": "#3E1F1D",
    "warn": "#E2A84B", "warn_soft": "#3A2E17",
    "sidebar": "#081317", "sidebar_hover": "#10242A", "sidebar_active": "#163A43",
    "sidebar_text": "#D5E6EA", "sidebar_muted": "#7E9AA1",
    "highlight": "#E9A23B", "highlight_soft": "#3A2E17", "hero": "#0B2F37",
}
MODE = "light"


def set_mode(mode: str) -> None:
    """Switch COLORS to the light or dark palette in place; rebuild the widgets afterwards."""
    global MODE
    MODE = "dark" if mode == "dark" else "light"
    COLORS.update(DARK if MODE == "dark" else LIGHT)


def apply(root) -> None:
    """Set the window background and the ttk styles used by the GUI.

    Styles: Primary / Secondary / Yes / No / Link .TButton, Card.TFrame,
    Panel.TFrame, CF.Horizontal.TProgressbar, and the default TCheckbutton,
    TRadiobutton, TEntry.
    """
    from tkinter import ttk

    c = COLORS
    root.configure(bg=c["bg"])
    root.option_add("*Font", FONTS["body"])
    for key, value in (("background", c["surface"]), ("foreground", c["text"]),
                       ("selectBackground", c["accent"]), ("selectForeground", c["on_accent"])):
        root.option_add(f"*TCombobox*Listbox.{key}", value)  # the drop-down list of comboboxes
    style = ttk.Style(root)
    style.theme_use("clam")  # the only built-in theme that accepts all colours

    style.configure(".", background=c["surface"], foreground=c["text"], font=FONTS["body"],
                    bordercolor=c["border"], lightcolor=c["surface"], darkcolor=c["surface"],
                    focuscolor=c["accent"])
    style.configure("TFrame", background=c["surface"])
    style.configure("Bg.TFrame", background=c["bg"])
    style.configure("Panel.TFrame", background=c["surface"], relief="solid", borderwidth=1)
    style.configure("TLabel", background=c["surface"], foreground=c["text"])

    def button(name, bg, fg, active, border=None, padding=(16, 6)):
        style.configure(name, background=bg, foreground=fg, font=FONTS["heading"],
                        bordercolor=border or bg, lightcolor=bg, darkcolor=bg, borderwidth=1,
                        padding=padding, relief="raised" if border else "flat", focusthickness=0)
        style.map(name,
                  background=[("disabled", c["chrome"]), ("pressed", active), ("active", active)],
                  foreground=[("disabled", c["muted"])],
                  lightcolor=[("pressed", active), ("active", active)],
                  darkcolor=[("pressed", active), ("active", active)])

    button("Primary.TButton", c["accent"], c["on_accent"], c["accent_hover"])
    button("Secondary.TButton", c["surface"], c["text"], c["chrome"], border=c["border"])
    button("Yes.TButton", c["ok"], c["on_accent"], "#256A42")
    button("No.TButton", c["danger"], c["on_accent"], "#931F18")
    button("Link.TButton", c["surface"], c["accent"], c["accent_soft"], padding=(8, 6))

    for name in ("TCheckbutton", "TRadiobutton"):
        style.configure(name, background=c["surface"], foreground=c["text"], font=FONTS["body"],
                        indicatorcolor=c["surface"], indicatorbackground=c["surface"])
        style.map(name,
                  background=[("active", c["surface"])],
                  indicatorcolor=[("selected", c["accent"]), ("pressed", c["accent_soft"])])

    style.configure("TEntry", fieldbackground=c["surface"], bordercolor=c["border"],
                    lightcolor=c["border"], darkcolor=c["border"], padding=(6, 4))
    style.map("TEntry", bordercolor=[("focus", c["accent"])], lightcolor=[("focus", c["accent"])])

    style.configure("CF.Horizontal.TProgressbar", troughcolor=c["chrome"], background=c["accent"],
                    bordercolor=c["chrome"], lightcolor=c["accent"], darkcolor=c["accent"],
                    thickness=8)
    style.configure("Treeview", background=c["surface"], fieldbackground=c["surface"],
                    foreground=c["text"], rowheight=28, bordercolor=c["border"], font=FONTS["body"])
    style.map("Treeview", background=[("selected", c["accent_soft"])],
              foreground=[("selected", c["text"])])
    style.configure("Treeview.Heading", background=c["bg"], foreground=c["muted"],
                    font=FONTS["small_bold"], relief="flat", bordercolor=c["border"], padding=(8, 6))
    style.map("Treeview.Heading", background=[("active", c["chrome"])])
    style.configure("TCombobox", fieldbackground=c["surface"], background=c["surface"],
                    bordercolor=c["border"], arrowcolor=c["muted"], padding=(6, 4))
    style.map("TCombobox", fieldbackground=[("readonly", c["surface"])],
              bordercolor=[("focus", c["accent"])])
    style.configure("Vertical.TScrollbar", background=c["chrome"], troughcolor=c["surface"],
                    bordercolor=c["surface"], arrowcolor=c["muted"])


def apply_matplotlib() -> None:
    """Make matplotlib charts match the GUI and the slides."""
    import matplotlib as mpl

    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [UI_FONT, "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.edgecolor": COLORS["border"],
        "axes.labelcolor": COLORS["text"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "axes.prop_cycle": mpl.cycler(color=[SUBSYSTEM_COLORS[s] for s in SUBSYSTEM_ORDER]),
        "grid.color": COLORS["bg"],
        "xtick.color": COLORS["muted"],
        "ytick.color": COLORS["muted"],
        "text.color": COLORS["text"],
        "figure.facecolor": "#FFFFFF",
        "axes.facecolor": "#FFFFFF",
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "legend.frameon": False,
    })
