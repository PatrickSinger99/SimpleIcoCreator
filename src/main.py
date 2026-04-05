import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import os
from tkinter.font import Font

from PIL.ImageOps import scale, expand

from utils import *


class App(tk.Tk):
    canvas_size = 360
    canvas_crop_pad = 60
    preview_size = 220
    min_scale = 0.1
    max_scale = 10
    file_explorer_bg = "#ffffff"
    border_color = "grey"
    border_width = 1

    def __init__(self, img_path):
        super().__init__()
        self.title("ICO Test")
        self.resizable(False, False)

        # Load image
        self.img_original = Image.open(img_path)  # for scaling/cropping
        self.img_tk = ImageTk.PhotoImage(self.img_original)  # for display
        self.img_base_name = os.path.basename(img_path).split(".")[0]
        self.img_parent_dir = os.path.dirname(img_path)

        # Transform tracking
        self.drag_start_x = None
        self.drag_start_y = None
        self.scale = 1.0

        self.total_delta_x = 0
        self.total_delta_y = 0

        """CROP SECTION"""

        # Layout column
        left_col_frame = tk.Frame(self, bg=App.border_color)
        left_col_frame.pack(side="left", fill="y", expand=True)

        # Crop Area Frame
        self.crop_frame = tk.Frame(left_col_frame)
        self.crop_frame.pack(side="top", padx=App.border_width, pady=App.border_width)

        # Canvas for image, checker, and crop area display
        self.crop_canvas = tk.Canvas(self.crop_frame, width=App.canvas_size, height=App.canvas_size,
                                     highlightthickness=0, cursor="fleur")
        self.crop_canvas.pack()

        self.crop_canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.crop_canvas.bind("<B1-Motion>", self.on_drag_move)
        self.crop_canvas.bind("<MouseWheel>", self.on_zoom)

        # Add checkerboard to canvas to signal transparency
        checkerboard = ImageTk.PhotoImage(create_checkerboard_pattern(App.canvas_size, App.canvas_size))
        self.crop_canvas.create_image(0, 0, anchor="nw", image=checkerboard)
        self.crop_canvas.checkerboard = checkerboard  # Keep reference

        # Main image display in canvas
        self.img_canvas = self.crop_canvas.create_image(0, 0, image=self.img_tk, anchor="nw")

        # Crop area display in canvas
        self.crop_xy1, self.crop_xy2 = App.canvas_crop_pad, App.canvas_size - App.canvas_crop_pad
        self.crop_canvas.create_rectangle(self.crop_xy1, self.crop_xy1, self.crop_xy2, self.crop_xy2, width=2)

        # Top
        x1, x2, w = self.crop_xy1, self.crop_xy2, App.canvas_size
        self.crop_canvas.create_rectangle(0, 0, w, x1, fill="black", stipple="gray50", outline="")
        self.crop_canvas.create_rectangle(0, x2, w, w, fill="black", stipple="gray50", outline="")
        self.crop_canvas.create_rectangle(0, x1, x1, x2, fill="black", stipple="gray50", outline="")
        self.crop_canvas.create_rectangle(x2, x1, w, x2, fill="black", stipple="gray50", outline="")

        # Layout column
        right_col_frame = tk.Frame(self, bg=App.border_color)
        right_col_frame.pack(side="right")

        """BORDER SECTION"""

        self.border_frame = tk.Frame(left_col_frame)
        self.border_frame.pack(side="top", padx=App.border_width, pady=(0, App.border_width), fill="both", expand="true")

        """PREVIEW SECTION"""

        # Frame for all preview views
        preview_border_frame = tk.Frame(right_col_frame, width=200, bg=App.file_explorer_bg)
        preview_border_frame.pack(side="top", padx=(0, App.border_width), pady=App.border_width)
        self.preview_frame = tk.Frame(preview_border_frame, bg=App.file_explorer_bg)
        self.preview_frame.pack()

        # Initial preview calculation
        self.img_cropped, self.img_preview_tk_large = None, None
        self.img_preview_tk_96, self.img_preview_tk_48, self.img_preview_tk_16 = None, None, None
        self.recalc_preview(disable_direct_update=True)

        # Large preview image
        tk.Label(self.preview_frame, text="Preview", bg=App.file_explorer_bg, font=Font(size=10)).pack(anchor="w", padx=10, pady=(3, 0))
        self.preview_img_display = tk.Label(self.preview_frame, image=self.img_preview_tk_large,
                                            bg=App.file_explorer_bg, bd=0)
        self.preview_img_display.pack()

        # Smaller previews
        small_preview_left_col = tk.Frame(self.preview_frame, bg=App.file_explorer_bg)
        small_preview_left_col.pack(fill="x", pady=(10, 3), padx=10)

        prev_96_frame = tk.Frame(small_preview_left_col, bg=App.file_explorer_bg)
        prev_96_frame.pack(side="left", padx=(0, 10))
        self.preview_img_96 = tk.Label(prev_96_frame, image=self.img_preview_tk_96, bg=App.file_explorer_bg, bd=0)
        self.preview_img_96.pack(side="top")
        tk.Label(prev_96_frame, text="Large Icon", font=Font(size=8), bg=App.file_explorer_bg).pack(side="top")

        small_preview_right_col = tk.Frame(small_preview_left_col, bg=App.file_explorer_bg)
        small_preview_right_col.pack(fill="y")

        prev_48_frame = tk.Frame(small_preview_right_col, bg=App.file_explorer_bg)
        prev_48_frame.pack(side="top", anchor="w")
        self.preview_img_48 = tk.Label(prev_48_frame, image=self.img_preview_tk_48, bg=App.file_explorer_bg, bd=0)
        self.preview_img_48.pack(side="left")
        tk.Label(prev_48_frame, text="Tiles & \nMedium Icon", font=Font(size=8), justify="left",
                 bg=App.file_explorer_bg).pack(side="left", anchor="n")

        prev_16_frame = tk.Frame(small_preview_right_col, bg=App.file_explorer_bg)
        prev_16_frame.pack(side="top", anchor="w", pady=(8, 0))
        self.preview_img_16 = tk.Label(prev_16_frame, image=self.img_preview_tk_16, bg=App.file_explorer_bg, bd=0)
        self.preview_img_16.pack(side="left")
        tk.Label(prev_16_frame, text="Small & Pinned Icon", font=Font(size=8), bg=App.file_explorer_bg).pack(side="left")


        """ACTION SECTION"""

        # Frame for all action buttons
        self.action_frame = tk.Frame(right_col_frame)
        self.action_frame.pack(side="bottom", fill="x", pady=(0, App.border_width), padx=(0, App.border_width))

        tk.Label(self.action_frame, text="Only save as file:").pack(anchor="w", padx=10, pady=(3, 0))

        save_only_col = tk.Frame(self.action_frame)
        save_only_col.pack(fill="x", padx=10)

        # Create only PNG
        self.create_png_btn = tk.Button(save_only_col, text="Save as PNG", command=self.save_as_png, cursor="hand2")
        self.create_png_btn.pack(side="left", fill="x", expand=True)

        # Create only ICO
        self.create_ico_btn = tk.Button(save_only_col, text="Save as ICO", command=self.save_as_ico, cursor="hand2")
        self.create_ico_btn.pack(side="left", fill="x", expand=True)

        tk.Label(self.action_frame, text="Save and set as folder icon:").pack(padx=10, pady=(10, 0), anchor="w")

        save_set_upper = tk.Frame(self.action_frame)
        save_set_upper.pack(fill="x", padx=10)

        # Set path for saving icon
        self.ico_path_var = tk.StringVar()
        self.ico_path_var.trace_add("write", self.on_ico_path_change)
        self.ico_save_path_entry = tk.Entry(save_set_upper, textvariable=self.ico_path_var)
        self.ico_save_path_entry.pack(side="left", fill="x", expand=True)

        # Folder selection for saving icon
        self.save_and_set_btn = tk.Button(save_set_upper, text="Explorer", cursor="hand2",
                                          command=self.on_select_ico_folder)
        self.save_and_set_btn.pack(side="right")

        save_set_lower = tk.Frame(self.action_frame)
        save_set_lower.pack(fill="x", padx=10, pady=(0, 10))

        # Select Parent Folder to set icon as
        self.save_and_set_parent_btn = tk.Button(save_set_lower, text="Set for Parent Folder", cursor="hand2",
                                                 command=self.on_set_ico_to_parent)
        self.save_and_set_parent_btn.pack(side="left", fill="x", expand=True)

        # Select Folder to set icon as
        self.save_and_set_select_btn = tk.Button(save_set_lower, text="Select Folder", cursor="hand2")
        self.save_and_set_select_btn.pack(side="left", fill="x", expand=True)

        self.on_ico_path_change()  # Initial validation

    def save_as_png(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")],
                                            initialfile=self.img_base_name)
        if not path:
            return

        self.img_cropped.save(path, "PNG")

    def save_as_ico(self):
        path = filedialog.asksaveasfilename(defaultextension=".ico", filetypes=[("ICO files", "*.ico")],
                                            initialfile=self.img_base_name)
        if not path:
            return
        print(path)
        convert_to_ico(self.img_cropped, output_path=path)

    def on_drag_start(self, e):
        # Set initial drag position
        self.drag_start_x = e.x
        self.drag_start_y = e.y

    def on_drag_move(self, e):
        # Calculate change to last state
        delta_x = e.x - self.drag_start_x
        delta_y = e.y - self.drag_start_y

        # Move image to new location
        self.crop_canvas.move(self.img_canvas, delta_x, delta_y)

        # Update last state to current state
        self.drag_start_x = e.x
        self.drag_start_y = e.y

        # Update total_delta_tracker
        self.total_delta_x += delta_x
        self.total_delta_y += delta_y

        self.recalc_preview()

    def on_zoom(self, e):

        # Determine zoom factor
        if e.delta > 0:
            zoom_factor = 1.1
        else:
            zoom_factor = 0.9

        # Update scale with clamping
        self.scale *= zoom_factor
        self.scale = max(App.min_scale, min(self.scale, App.max_scale))

        # Get current image position on canvas
        img_x, img_y = self.crop_canvas.coords(self.img_canvas)

        # Resize tk image from original
        new_w = int(self.img_original.width * self.scale)
        new_h = int(self.img_original.height * self.scale)

        pil_resized = self.img_original.resize((new_w, new_h), Image.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(pil_resized)

        # Update canvas object
        self.crop_canvas.itemconfig(self.img_canvas, image=self.img_tk)

        # Compute new position so zoom centers on cursor
        new_x = e.x - (e.x - img_x) * zoom_factor
        new_y = e.y - (e.y - img_y) * zoom_factor

        self.crop_canvas.coords(self.img_canvas, new_x, new_y)

        # Update delta tracking (IMPORTANT: overwrite, don't add)
        self.total_delta_x = new_x
        self.total_delta_y = new_y

        self.recalc_preview()

    def recalc_preview(self, disable_direct_update=False):
        self.img_cropped = crop_img(self.img_original, self.crop_xy1, self.crop_xy2, self.total_delta_x,
                                    self.total_delta_y, self.scale)

        # Resize large preview
        resized_crop_preview = self.img_cropped.resize((App.preview_size, App.preview_size), Image.LANCZOS)
        self.img_preview_tk_large = ImageTk.PhotoImage(resized_crop_preview)

        # Resize smaller previews
        self.img_preview_tk_96 = ImageTk.PhotoImage(resized_crop_preview.resize((96, 96), Image.LANCZOS))
        self.img_preview_tk_48 = ImageTk.PhotoImage(resized_crop_preview.resize((48, 48), Image.LANCZOS))
        self.img_preview_tk_16 = ImageTk.PhotoImage(resized_crop_preview.resize((16, 16), Image.LANCZOS))

        if not disable_direct_update:
            self.preview_img_display.config(image=self.img_preview_tk_large)
            self.preview_img_96.config(image=self.img_preview_tk_96)
            self.preview_img_48.config(image=self.img_preview_tk_48)
            self.preview_img_16.config(image=self.img_preview_tk_16)

    def on_select_ico_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.ico_path_var.set(path)

    def on_ico_path_change(self, *args):
        path = self.ico_path_var.get()

        if os.path.isdir(path):
            # valid
            self.ico_save_path_entry.config(fg="black")

            # Enable action buttons
            self.save_and_set_parent_btn.config(state="normal", cursor="hand2")
            self.save_and_set_select_btn.config(state="normal", cursor="hand2")
        else:
            # invalid
            self.ico_save_path_entry.config(fg="red")

            # Disable action buttons
            self.save_and_set_parent_btn.config(state="disabled", cursor="")
            self.save_and_set_select_btn.config(state="disabled", cursor="")

    def on_set_ico_to_parent(self):
        ico_path = os.path.join(self.ico_path_var.get(), f"{self.img_base_name}.ico")
        convert_to_ico(self.img_cropped, output_path=ico_path)
        set_folder_icon(self.img_parent_dir, ico_path)


if __name__ == '__main__':
    app = App(r"E:\GitHub Repositories\SimpleIcoCreator\examples\meowl.jpg")
    app.mainloop()

