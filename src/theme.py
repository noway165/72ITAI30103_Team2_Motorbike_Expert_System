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

COLORS = {  # MotoLogic palette (docs/design/motologic_spec.md); keys kept for older screens
    "accent": "#1F6B57",        # emphasised text, border of a selected card, stepper line
    "accent_hover": "#17543F",  # primary button when hovered / pressed
    "accent_soft": "#E3EFE7",   # "why" box, selected item
    "bg": "#F2F3EC",            # window background (cream)
    "surface": "#FFFFFF",       # white rounded cards, entries
    "chrome": "#E7EAE0",        # chips, CF bar trough, disabled button
    "border": "#DCE1D6",        # 1 px border of cards and entries
    "text": "#14352C",
    "muted": "#5F6F67",         # hints, counts, status bar text
    "on_accent": "#FFFFFF",     # text on accent / ok / danger
    "ok": "#2E7D4F",            # severity "self", Yes button, Wang agrees
    "ok_soft": "#E3F1E8",
    "danger": "#B3261E",        # severity "mechanic", No button, errors
    "danger_soft": "#F8E1DF",
    "warn": "#8A5A00",          # not enough evidence for any fault
    "warn_soft": "#FBEFD6",
    "sidebar": "#FFFFFF",       # left navigation (light, as in the MotoLogic design)
    "sidebar_hover": "#F2F3EC",
    "sidebar_active": "#DDF57A",
    "sidebar_text": "#14352C",
    "sidebar_muted": "#5F6F67",
    "highlight": "#A9C93A",     # title underline, highlighted words
    "highlight_soft": "#EEF7CF",
    "hero": "#1B3B33",          # dark banners
    "panel": "#1B3B33",         # dark moss blocks: right-hand panels, number cards, result banner
    "panel_soft": "#24493F",    # box inside a dark block
    "on_panel": "#FFFFFF",      # text on panel
    "panel_muted": "#B9CCC4",   # secondary text on panel
    "lime": "#DDF57A",          # selected nav item, arrow buttons, highlighted numbers
    "lime_soft": "#EEF7CF",     # selected card, "Recommended" chip
    "on_lime": "#14352C",       # text on lime
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
    "forward": "#0E5E6F",
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
    "hero": (UI_FONT, 26, "bold"),      # MotoLogic screen titles
    "big": (UI_FONT, 21, "bold"),       # MotoLogic question, fault name, big numbers
    "h2": (UI_FONT, 15, "bold"),        # MotoLogic card titles
    "lead": (UI_FONT, 11),              # MotoLogic subtitles and body
    "eyebrow": (UI_FONT, 9, "bold"),    # small capital label above a title
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

WINDOW_SIZE = (1280, 820)
WINDOW_MIN_SIZE = (1040, 660)
SIDEBAR_WIDTH = 236
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
    "accent": "#4FB394", "accent_hover": "#6CC7AA", "accent_soft": "#1E3A30",
    "bg": "#0F1B17", "surface": "#17261F", "chrome": "#22342C", "border": "#2C4038",
    "text": "#E3EEEA", "muted": "#93A9A0", "on_accent": "#0B1612",
    "ok": "#4CB57F", "ok_soft": "#173A28", "danger": "#E5675E", "danger_soft": "#3E1F1D",
    "warn": "#E2A84B", "warn_soft": "#3A2E17",
    "sidebar": "#0B1612", "sidebar_hover": "#17261F", "sidebar_active": "#C9E86A",
    "sidebar_text": "#E3EEEA", "sidebar_muted": "#93A9A0",
    "highlight": "#C9E86A", "highlight_soft": "#26341C", "hero": "#0B1612",
    "panel": "#0B1612", "panel_soft": "#16271F", "on_panel": "#E6F0EC", "panel_muted": "#8FA89F",
    "lime": "#C9E86A", "lime_soft": "#26341C", "on_lime": "#0F1B17",
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
