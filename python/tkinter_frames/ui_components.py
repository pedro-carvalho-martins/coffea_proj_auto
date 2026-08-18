import tkinter as tk

from tkinter_frames.ui_theme import (
    BUTTON_IPADY,
    COLORS,
    CONTENT_WRAP,
    FONT_AMOUNT,
    FONT_BUTTON,
    FONT_NORMAL,
    FONT_RESULT_MESSAGE,
    FONT_RESULT_TITLE,
    FONT_SECONDARY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPACE_MD,
)


def create_screen(parent, background=None):
    return tk.Frame(
        parent,
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        bg=background or COLORS["background"],
    )


def create_touch_button(
    parent,
    text,
    command,
    variant="normal",
    font=FONT_BUTTON,
    wraplength=260,
):
    palettes = {
        "normal": (
            COLORS["surface"],
            COLORS["text"],
            COLORS["surface_alt"],
            COLORS["text"],
            COLORS["divider"],
        ),
        "primary": (
            COLORS["accent"],
            COLORS["white"],
            COLORS["accent_pressed"],
            COLORS["white"],
            COLORS["accent"],
        ),
        "danger": (
            COLORS["danger"],
            COLORS["white"],
            COLORS["danger_pressed"],
            COLORS["white"],
            COLORS["danger"],
        ),
    }
    background, foreground, active_background, active_foreground, border = palettes[variant]
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=font,
        wraplength=wraplength,
        bg=background,
        fg=foreground,
        activebackground=active_background,
        activeforeground=active_foreground,
        disabledforeground=COLORS["text_secondary"],
        relief=tk.FLAT,
        bd=0,
        highlightthickness=1,
        highlightbackground=border,
        highlightcolor=border,
        takefocus=False,
    )


def format_brl(value):
    return ("R$ {:.2f}".format(value)).replace(".", ",")


def create_amount_display(parent, value, label="Valor selecionado:"):
    frame = tk.Frame(parent, bg=COLORS["background"])
    tk.Label(
        frame,
        text=label,
        font=FONT_NORMAL,
        bg=COLORS["background"],
        fg=COLORS["text_secondary"],
    ).pack()
    tk.Label(
        frame,
        text=format_brl(value),
        font=FONT_AMOUNT,
        bg=COLORS["background"],
        fg=COLORS["text"],
    ).pack(pady=(0, 2))
    return frame


class StatusCard:
    def __init__(self, parent, title):
        self.frame = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["divider"],
        )
        self.frame.columnconfigure(1, weight=1)
        self.icon_label = tk.Label(
            self.frame,
            bg=COLORS["surface"],
        )
        self.icon_label.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(SPACE_MD, 10),
            pady=SPACE_MD,
        )
        tk.Label(
            self.frame,
            text=title,
            font=FONT_SECONDARY,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            wraplength=220,
            justify=tk.LEFT,
            anchor=tk.W,
        ).grid(row=0, column=1, sticky=tk.SW, padx=(0, SPACE_MD), pady=(9, 0))
        self.status_label = tk.Label(
            self.frame,
            text="Verificando...",
            font=("SegoeUI", 12, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"],
            anchor=tk.W,
        )
        self.status_label.grid(
            row=1,
            column=1,
            sticky=tk.NW,
            padx=(0, SPACE_MD),
            pady=(1, 9),
        )

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def set_state(self, image, text, state):
        colors = {
            "loading": COLORS["text_secondary"],
            "success": COLORS["success"],
            "disabled": COLORS["text_secondary"],
            "error": COLORS["danger"],
        }
        self.icon_label.configure(image=image)
        self.status_label.configure(text=text, fg=colors[state])


def create_result_screen(
    parent,
    title,
    message="",
    background=None,
    foreground=None,
    button_text=None,
    button_command=None,
):
    background = background or COLORS["background"]
    foreground = foreground or COLORS["text"]
    frame = create_screen(parent, background)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    content = tk.Frame(frame, bg=background)
    content.grid(row=0, column=0, sticky=tk.NSEW, padx=18, pady=28)
    content.columnconfigure(0, weight=1)
    content.rowconfigure(0, weight=1)
    content.rowconfigure(3, weight=1)

    title_label = tk.Label(
        content,
        text=title,
        font=FONT_RESULT_TITLE,
        bg=background,
        fg=foreground,
        wraplength=CONTENT_WRAP,
        justify=tk.CENTER,
    )
    title_label.grid(row=1, column=0, sticky=tk.EW, pady=(0, 12))

    message_label = tk.Label(
        content,
        text=message,
        font=FONT_RESULT_MESSAGE,
        bg=background,
        fg=foreground,
        wraplength=CONTENT_WRAP,
        justify=tk.CENTER,
    )
    message_label.grid(row=2, column=0, sticky=tk.EW)
    frame.status_title_label = title_label
    frame.status_message_label = message_label

    if button_text and button_command:
        button = create_touch_button(
            content,
            button_text,
            button_command,
            variant="normal",
            font=("Ubuntu", 13, "bold"),
            wraplength=245,
        )
        button.grid(
            row=4,
            column=0,
            sticky=tk.EW,
            pady=(18, 0),
            ipady=BUTTON_IPADY,
        )
        frame.status_button = button

    return frame


def create_instruction_screen(parent, title, message=""):
    frame = create_screen(parent)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = tk.Frame(
        frame,
        bg=COLORS["surface"],
        highlightthickness=1,
        highlightbackground=COLORS["divider"],
    )
    card.grid(row=0, column=0, sticky=tk.NSEW, padx=16, pady=24)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(0, weight=1)
    card.rowconfigure(4, weight=1)

    title_label = tk.Label(
        card,
        text=title,
        font=("SegoeUI", 20, "bold"),
        bg=COLORS["surface"],
        fg=COLORS["text"],
        wraplength=260,
        justify=tk.CENTER,
    )
    title_label.grid(row=1, column=0, padx=12, pady=(0, 22))

    divider = tk.Frame(card, height=1, bg=COLORS["divider"])
    divider.grid(row=2, column=0, sticky=tk.EW, padx=22)

    message_label = tk.Label(
        card,
        text=message,
        font=FONT_SECONDARY,
        bg=COLORS["surface"],
        fg=COLORS["text_secondary"],
        wraplength=250,
        justify=tk.CENTER,
    )
    message_label.grid(row=3, column=0, padx=12, pady=(22, 0))
    frame.status_title_label = title_label
    frame.status_message_label = message_label
    return frame
