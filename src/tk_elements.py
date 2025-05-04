import tkinter as tk
from tkinterdnd2 import DND_FILES  # https://pypi.org/project/tkinterdnd2/
from typing import Optional, Callable, Tuple
from dataclasses import dataclass


@dataclass
class BtnPalette:

    @dataclass
    class ColorState:
        base: str
        hover: str
        active: str

    bg: ColorState
    border: ColorState
    text: ColorState

    def __init__(self,
                 bg: Tuple[str, str, str],
                 border: Tuple[str, str, str],
                 text: Tuple[str, str, str]):
        self.bg = self.ColorState(*bg)
        self.border = self.ColorState(*border)
        self.text = self.ColorState(*text)

    @classmethod
    def green(cls):
        return cls(
            bg=("#90C67C", "#67AE6E", "#328E6E"),
            border=("#67AE6E", "#67AE6E", "#328E6E"),
            text=("#328E6E", "#328E6E", "white")
        )

    @classmethod
    def green_light(cls):
        return cls(
            bg=("#E1EEBC", "#67AE6E", "#328E6E"),
            border=("#67AE6E", "#67AE6E", "#328E6E"),
            text=("black", "black", "black")
        )

    @classmethod
    def red(cls):
        return cls(
            bg=("#FF7275", "#FF4546", "#FF3538"),
            border=("#FF4546", "#FF4546", "#FF3538"),
            text=("black", "black", "black")
        )

class BorderBtn(tk.Frame):
    def __init__(self, master=None, palette: BtnPalette = None, border_width: int = 1, **kwargs):
        if palette is None:
            palette = BtnPalette.green()
        self.palette = palette

        super().__init__(master, bg=palette.border.base)

        self.btn = tk.Button(self, relief="flat", cursor="hand2", bd=0,
                             bg=self.palette.bg.base,
                             fg=self.palette.text.base,
                             activebackground=self.palette.bg.active,
                             activeforeground=self.palette.text.active,
                             **kwargs)
        self.btn.pack(pady=border_width, padx=border_width, fill="both")

        # Bind hover to the frame, not the button directly
        self.bind("<Enter>", self._on_enter, add="+")
        self.bind("<Leave>", self._on_leave, add="+")
        self.btn.bind("<Enter>", self._on_enter, add="+")
        self.btn.bind("<Leave>", self._on_leave, add="+")
        self.btn.bind("<ButtonPress-1>", self._on_press, add="+")
        self.btn.bind("<ButtonRelease-1>", self._on_release, add="+")

    def _on_enter(self, event=None):
        self.btn.config(bg=self.palette.bg.hover, fg=self.palette.text.hover)
        self.config(bg=self.palette.border.hover)

    def _on_leave(self, event=None):
        # Only reset if the mouse is really outside the entire widget
        x, y = self.winfo_pointerxy()
        widget_under_cursor = self.winfo_containing(x, y)
        if widget_under_cursor not in (self, self.btn):
            self.btn.config(bg=self.palette.bg.base, fg=self.palette.text.base)
            self.config(bg=self.palette.border.base)

    def _on_press(self, event=None):
        super().config(bg=self.palette.border.active)

    def _on_release(self, event=None):
        # Update to match hover or base depending on cursor position
        x, y = self.winfo_pointerxy()
        widget_under_cursor = self.winfo_containing(x, y)
        if widget_under_cursor in (self, self.btn):
            super().config(bg=self.palette.border.hover)
        else:
            super().config(bg=self.palette.border.base)

    def __getitem__(self, key):
        return self.btn[key]

    def __setitem__(self, key, value):
        self.btn[key] = value


class DnDFileLabel(tk.Label):
    def __init__(self, *args, on_drag_enter: Optional[Callable] = None, on_drag_leave: Optional[Callable] = None,
                 on_drop: Optional[Callable] = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.drop_target_register(DND_FILES)

        if on_drag_enter:
            self.dnd_bind('<<DropEnter>>', on_drag_enter)
        if on_drag_leave:
            self.dnd_bind('<<DropLeave>>', on_drag_leave)
        if on_drop:
            self.dnd_bind('<<Drop>>', on_drop)


class DnDFileCanvas(tk.Canvas):
    def __init__(self, *args, on_drag_enter: Optional[Callable] = None, on_drag_leave: Optional[Callable] = None,
                 on_drop: Optional[Callable] = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.drop_target_register(DND_FILES)

        if on_drag_enter:
            self.dnd_bind('<<DropEnter>>', on_drag_enter)
        if on_drag_leave:
            self.dnd_bind('<<DropLeave>>', on_drag_leave)
        if on_drop:
            self.dnd_bind('<<Drop>>', on_drop)

