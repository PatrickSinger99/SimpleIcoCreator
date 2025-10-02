import tkinter as tk
from tkinterdnd2 import DND_FILES  # https://pypi.org/project/tkinterdnd2/
from typing import Optional, Callable, Tuple, Union, List
from dataclasses import dataclass
from tkinter import ttk
from PIL import Image, ImageTk


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
            bg=("#8CCC29", "#78B714", "#69A011"),
            border=("#78B714", "#69A011", "#69A011"),
            text=("white", "white", "white")
        )

    @classmethod
    def green_light(cls):
        return cls(
            bg=("white", "#EBFFC9", "#B1CC86"),
            border=("#78B714", "#69A011", "#69A011"),
            text=("#78B714", "#78B714", "white")
        )

    @classmethod
    def red(cls):
        return cls(
            bg=("#FF7275", "#FF4546", "#FF3538"),
            border=("#FF4546", "#FF4546", "#FF3538"),
            text=("black", "black", "black")
        )

    @classmethod
    def red_light(cls):
        return cls(
            bg=("white", "#FF4546", "#FF3538"),
            border=("#FF4546", "#FF4546", "#FF3538"),
            text=("#FF4546", "#FF4546", "black")
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

    # --- Proxy methods ---
    def btn_config(self, cnf=None, **kwargs):
        """Redirect config to inner button"""
        return self.btn.config(cnf, **kwargs)

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


class MultiCheckSelector(tk.Frame):
    def __init__(self, parent, values, defaults: Union[List[bool], bool] = True, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.vars = {}
        for i, size in enumerate(values):
            var = tk.BooleanVar(value=defaults[i] if type(defaults) is List else defaults)
            chk = ttk.Checkbutton(self, text=size, variable=var)
            chk.grid(row=0, column=i)
            self.vars[size] = var

    def get_selected_sizes(self):
        return [size for size, var in self.vars.items() if var.get()]


class CropCanvas(DnDFileCanvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Crop state
        self.crop_rect = None
        self.crop_start = None
        self.crop_box = None
        self.crop_mode_active = False
        self.force_square_crop = True

        # Image state
        self.displayed_img_path = None
        self.tk_img = None
        self.preview_size = kwargs.get("width", 320)  # fallback

    def enable_crop_mode(self):
        """Activate crop selection mode"""
        self.bind("<ButtonPress-1>", self._on_crop_start)
        self.bind("<B1-Motion>", self._on_crop_drag)
        self.bind("<ButtonRelease-1>", self._on_crop_end)

        self.crop_mode_active = True

    def disable_crop_mode(self):
        """Disable crop selection mode"""
        self.unbind("<ButtonPress-1>")
        self.unbind("<B1-Motion>")
        self.unbind("<ButtonRelease-1>")

    def reset_crop(self):
        self.disable_crop_mode()
        self.crop_mode_active = False

        if self.crop_rect:
            self.delete(self.crop_rect)
            self.crop_rect = None

        self.crop_start = None
        self.crop_box = None

    def _on_crop_start(self, event):
        self.crop_start = (event.x, event.y)
        if self.crop_rect:
            self.delete(self.crop_rect)
        self.crop_rect = self.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline="red", width=2, dash=(4, 2)
        )

    def _on_crop_drag(self, event):
        if self.crop_start and self.crop_rect:
            x0, y0 = self.crop_start
            x1, y1 = event.x, event.y

            if self.force_square_crop:
                dx = x1 - x0
                dy = y1 - y0
                side = min(abs(dx), abs(dy))
                x1 = x0 + side * (1 if dx >= 0 else -1)
                y1 = y0 + side * (1 if dy >= 0 else -1)

            self.coords(self.crop_rect, x0, y0, x1, y1)

    def _on_crop_end(self, event):
        if self.crop_start and self.crop_rect:
            x1, y1, x2, y2 = self.coords(self.crop_rect)
            self.crop_box = (min(x1, x2), min(y1, y2),
                             max(x1, x2), max(y1, y2))
            print("Crop box set:", self.crop_box)

    def set_image(self, img_path, preview_size=None):
        """Load and display an image in the canvas"""
        from utils import load_img  # your existing helper
        if preview_size:
            self.preview_size = preview_size
        img = load_img(img_path, set_size=self.preview_size)
        self.tk_img = ImageTk.PhotoImage(img)
        center = int(self.preview_size / 2)
        self.create_image(center, center, anchor=tk.CENTER, image=self.tk_img)
        self.displayed_img_path = img_path

    def get_cropped_image(self, min_size=256):
        if not self.displayed_img_path:
            return None

        img = Image.open(self.displayed_img_path)
        orig_w, orig_h = img.size

        if not self.crop_box:

            if img.width < min_size or img.height < min_size:
                img = img.resize((max(min_size, img.width), max(min_size, img.height)), resample=Image.LANCZOS)

            return img

        # Determine displayed image size on the canvas
        canvas_w = self.preview_size
        canvas_h = self.preview_size
        scale = min(canvas_w / orig_w, canvas_h / orig_h)
        disp_w = int(orig_w * scale)
        disp_h = int(orig_h * scale)

        # Compute offsets (if image is centered in canvas)
        offset_x = (canvas_w - disp_w) // 2
        offset_y = (canvas_h - disp_h) // 2

        # Map canvas crop box to original image coordinates
        x1, y1, x2, y2 = self.crop_box
        real_box = (
            int((x1 - offset_x) / scale),
            int((y1 - offset_y) / scale),
            round((x2 - offset_x) / scale),  # use round for right/bottom
            round((y2 - offset_y) / scale)
        )

        cropped_img = img.crop(real_box)

        # If the crop is smaller than minimum size, scale it up
        if cropped_img.width < min_size or cropped_img.height < min_size:
            cropped_img = cropped_img.resize((max(min_size, cropped_img.width), max(min_size, cropped_img.height)),
                                             resample=Image.LANCZOS)

        return cropped_img

