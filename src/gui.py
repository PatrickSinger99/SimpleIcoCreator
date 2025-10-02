import tkinter as tk
from gettext import textdomain
from tkinter import ttk
from PIL.ImageOps import expand
from tkinterdnd2 import DND_FILES, TkinterDnD  # https://pypi.org/project/tkinterdnd2/
from typing import Optional, Callable
from utils import *
from tk_elements import *
from PIL import ImageTk
import re
from tkinter.font import Font
import os
from collections import deque
from styles import init_styles
from tkinter import filedialog


class App(TkinterDnD.Tk):
    img_preview_size = 320
    img_queue_size = 50
    valid_img_types = ("jpg", "jpeg", "png", "webp", "gif")
    cols = {"dnd_border_base": "grey", "dnd_border_valid": "#8CCC29", "dnd_border_invalid": "indian red",
            "action_btn_base": "#90C67C", "action_btn_hover": "#67AE6E", "action_btn_press": "#328E6E"}

    def __init__(self):
        super().__init__()
        self.title("Simple Ico Converter")
        self.resizable(False, False)
        self.iconbitmap("./imgs/app_icon.ico")

        """IMAGE AREA """

        # FRAME: Highest frame for all image related elements
        self.content_frame = tk.Frame(self, bg="light grey", width=200)
        self.content_frame.pack(side="top", fill="x")

        self.left_wing_frame = tk.Frame(self.content_frame, bg=self.content_frame.cget("bg"), width=220)
        self.left_wing_frame.pack(side="left", anchor="n", pady=10, padx=10, fill="y")
        self.left_wing_frame.pack_propagate(False)

        self.queue_frame = tk.Frame(self.left_wing_frame, bg=self.left_wing_frame.cget("bg"), width=200)
        self.queue_frame.pack(side="right", anchor="n")

        self.outer_dnd_frame = tk.Frame(self.content_frame, bg=self.content_frame.cget("bg"))
        self.outer_dnd_frame.pack(side="left", pady=10)

        # Border for main image area
        self.dnd_border_frame = tk.Frame(self.outer_dnd_frame, bg=App.cols["dnd_border_base"])
        self.dnd_border_frame.pack()

        # Main image DnD area
        self.dnd_area = CropCanvas(self.dnd_border_frame, on_drag_enter=self.on_drag_enter,
                                      on_drag_leave=self.on_drag_leave, on_drop=self.on_drop,
                                      height=App.img_preview_size, width=App.img_preview_size,
                                      bg="grey", bd=0, relief='ridge', highlightthickness=0)
        self.dnd_area.pack(padx=1, pady=1)

        # Add checkerboard to canvas to signal transparency
        checkerboard = ImageTk.PhotoImage(create_checkerboard_pattern(App.img_preview_size, App.img_preview_size))
        self.dnd_area.create_image(0, 0, anchor="nw", image=checkerboard)
        self.dnd_area.checkerboard = checkerboard  # Keep reference

        # Image Infos
        self.dnd_img_info_frame = tk.Frame(self.outer_dnd_frame, bg=self.outer_dnd_frame.cget("bg"))
        self.dnd_img_info_frame.pack(fill="x")

        self.dnd_img_info_dims = tk.Label(self.dnd_img_info_frame, bg=self.dnd_img_info_frame.cget("bg"), fg="grey")
        self.dnd_img_info_dims.pack(side="left")

        self.dnd_img_info_name = tk.Label(self.dnd_img_info_frame, bg=self.dnd_img_info_frame.cget("bg"), fg="grey")
        self.dnd_img_info_name.pack(side="left")

        self.dnd_img_info_remove_btn = tk.Button(self.dnd_img_info_frame, text="Clear", command=self.load_from_queue,
                                                 bg=self.dnd_img_info_frame.cget("bg"), relief="flat", cursor="hand2",
                                                 bd=0, activebackground=self.dnd_img_info_frame.cget("bg"), fg="grey")
        self.dnd_img_info_remove_btn.pack(side="right")

        self.right_wing_frame = tk.Frame(self.content_frame, bg=self.content_frame.cget("bg"), width=220)
        self.right_wing_frame.pack(side="left", anchor="n", pady=10, padx=10, fill="both", expand=True)
        self.right_wing_frame.pack_propagate(False)

        self.toggle_crop_btn = BorderBtn(master=self.right_wing_frame, text="Crop Image", palette=BtnPalette.green_light(),
                                         command=self.toggle_crop_mode)
        self.toggle_crop_btn.pack(side="top", anchor="n", fill="x", expand=True)

        self.preview_frame = tk.Frame(self.right_wing_frame)
        self.preview_frame.pack(side="bottom")

        self.preview_image = tk.Frame(self.preview_frame)
        self.preview_image.pack()

        """SETTINGS FOOTER"""

        tk.Frame(self, bg="grey").pack(side="top", fill="x")  # Border

        # FRAME: Highest frame for all user settings related elements
        self.settings_frame = tk.Frame(self, bg="dark grey", height=40)
        self.settings_frame.pack(side="bottom", fill="x")

        # FRAMES: Left parameter configuration spaces
        self.parameter_frame = tk.Frame(self.settings_frame, bg=self.settings_frame.cget("bg"))
        self.parameter_frame.pack(side="left", fill="both", expand=True)
        self.upper_param_frame = tk.Frame(self.parameter_frame, bg=self.parameter_frame.cget("bg"))
        self.upper_param_frame.pack(side="top", fill="y", expand=True, anchor="w", padx=4, pady=(4, 0))
        self.lower_param_frame = tk.Frame(self.parameter_frame, bg=self.parameter_frame.cget("bg"))
        self.lower_param_frame.pack(side="bottom", fill="y", expand=True, anchor="w", padx=4, pady=(0, 4))

        # Title Label
        tk.Label(self.lower_param_frame, text="Save Path", bg=self.lower_param_frame.cget("bg")).pack(side="top", anchor="w")

        # FRAME: Contains all elements displaying the target path
        self.set_path_frame = tk.Frame(self.lower_param_frame, bg=self.lower_param_frame.cget("bg"))
        self.set_path_frame.pack(side="top", anchor="w")

        # PATH: Directory path entry
        self.path_entry_var = tk.StringVar()
        self.path_entry = ttk.Entry(self.set_path_frame, width=60, textvariable=self.path_entry_var)
        self.path_entry.pack(side="left")

        tk.Label(self.set_path_frame, text="/", font=Font(size=11), bg=self.set_path_frame.cget("bg")).pack(side="left")  # Backslash symbol

        # PATH: Ico name entry
        self.file_name_entry_var = tk.StringVar()
        self.file_name_entry = ttk.Entry(self.set_path_frame, width=20, textvariable=self.file_name_entry_var)
        self.file_name_entry.pack(side="left")

        tk.Label(self.set_path_frame, text=".ico", font=Font(size=11), bg=self.set_path_frame.cget("bg")).pack(side="left")  # .ico symbol

        # FRAME: Contains all buttons for converting
        self.action_frame = tk.Frame(self.settings_frame, bg=self.settings_frame.cget("bg"))
        self.action_frame.pack(side="right")

        # CONVERT: Single image
        self.single_convert_btn = BorderBtn(master=self.action_frame, text="Save as ICO",
                                            command=self.on_single_convert_btn, height=2, border_width=1)
        self.single_convert_btn.grid(row=0, column=0, sticky="ew", pady=4, padx=(4, 2))

        # CONVERT: Single image and set as icon to folder
        self.convert_and_set_btn = BorderBtn(self.action_frame, text="Save and set as icon", height=2,
                                             command=self.on_convert_and_set_btn, border_width=1)
        self.convert_and_set_btn.grid(row=0, column=1, sticky="ew", pady=4, padx=(2, 4))

        # CONVERT: All loaded images
        self.all_convert_button = BorderBtn(self.action_frame, palette=BtnPalette.green_light(), border_width=1,
                                            text="Apply transforms and save all as ICO",
                                            command=self.on_all_convert_button)
        self.all_convert_button.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(0, 4))

        tk.Frame(self.settings_frame, bg="grey").pack(side="right", fill="y")  # Border

        """VARIABLES"""

        self.displayed_img = None  # Image currently in the main display
        self.image_queue = deque()  # Images currently in the queue
        self.queue_tk_img_obj = {}

        """INITS"""

        self.bind_all("<Button-1>", self.clear_focus, add="+")  # `add='+'` keeps existing bindings intact

    def clear_focus(self, event):
        """Clear focus if clicked widget is not an input"""
        non_focusable = (tk.Frame, tk.Label, tk.Canvas, tk.Toplevel)  # Add types as needed
        widget = event.widget

        # Only clear focus if clicked widget is one of the non-focusable types
        if isinstance(widget, non_focusable):
            self.focus_set()

    def toggle_crop_mode(self, force_deactivate=False):

        if force_deactivate or self.dnd_area.crop_mode_active:
            self.dnd_area.reset_crop()
            self.toggle_crop_btn.btn_config(text="Crop Image")
            self.toggle_crop_btn.palette = BtnPalette.green_light()

        else:
            self.dnd_area.enable_crop_mode()
            self.toggle_crop_btn.btn_config(text="Reset Crop")
            self.toggle_crop_btn.palette = BtnPalette.red_light()

    def get_entry_path(self):
        return os.path.join(self.path_entry_var.get(), self.file_name_entry_var.get() + ".ico")

    def on_single_convert_btn(self):

        if self.displayed_img is not None:
            convert_to_ico(pil_obj=self.dnd_area.get_cropped_image(), output_path=self.get_entry_path())

        self.toggle_crop_mode(force_deactivate=True)
        self.load_from_queue()

    def on_convert_and_set_btn(self):
        out_path = self.get_entry_path()

        if self.displayed_img is not None:
            convert_to_ico(pil_obj=self.dnd_area.get_cropped_image(), output_path=out_path)

        folder_path = filedialog.askdirectory(title="Select a folder")

        if folder_path:
            set_folder_icon(folder_path, out_path)

        self.toggle_crop_mode(force_deactivate=True)
        self.load_from_queue()

    def on_all_convert_button(self):
        pass

    def update_save_path_entries(self, path):

        if os.path.isfile(path):
            filename = os.path.splitext(os.path.basename(path))[0]
            path = os.path.dirname(path)
            self.file_name_entry_var.set(filename)
        elif path == "":  # RESET
            self.file_name_entry_var.set("")

        self.path_entry_var.set(path)

    @staticmethod
    def validate_file_drop(data):
        matches = re.findall(r'\{([^}]+)\}|([^\s]+)', data)
        paths = [m[0] or m[1] for m in matches]
        valid_paths = [p for p in paths if p.split(".")[-1].lower() in App.valid_img_types]
        print("Extracted valid paths:", valid_paths)
        return valid_paths

    def on_drag_enter(self, event):
        print("Data is hovering over frame:", repr(event.data))

        valid_paths = self.validate_file_drop(event.data)
        if len(valid_paths) != 0:
            self.dnd_border_frame.config(bg=App.cols["dnd_border_valid"])
        else:
            self.dnd_border_frame.config(bg=App.cols["dnd_border_invalid"])

    def on_drag_leave(self, event):
        print("Data left the frame:", repr(event.data))
        self.dnd_border_frame.config(bg=App.cols["dnd_border_base"])

    def on_drop(self, event):
        print("Data dropped:", repr(event.data))
        valid_paths = self.validate_file_drop(event.data)

        if len(valid_paths) == 0:
            pass
        elif not self.displayed_img:
            self.load_main_display(path=valid_paths[0])
            self.add_to_queue(valid_paths[1:]) if len(valid_paths) > 1 else None
        else:
            self.add_to_queue(valid_paths)

        self.dnd_border_frame.config(bg=App.cols["dnd_border_base"])

    def load_main_display(self, path):
        img = load_img(path, set_size=App.img_preview_size)
        tk_img = ImageTk.PhotoImage(img)
        center = int(App.img_preview_size / 2)
        self.dnd_area.create_image(center, center, anchor=tk.CENTER, image=tk_img)
        self.dnd_area.image = tk_img  # Keep reference
        self.dnd_area.displayed_img_path = path
        self.update_save_path_entries(path)
        self.displayed_img = path
        self.update_dnd_img_infos()

    def update_dnd_img_infos(self):
        try:
            w, h = Image.open(self.displayed_img).size
            self.dnd_img_info_dims.config(text=f"{w} x {h}")

            base_name = os.path.basename(self.displayed_img)
            display_name = base_name if len(base_name) < 32 else base_name[:30] + "..."

            self.dnd_img_info_name.config(text=os.path.basename(display_name))
        except Exception as e:

            print("Could not update image info:", e)
            self.dnd_img_info_dims.config(text="")
            self.dnd_img_info_name.config(text="")

    def add_to_queue(self, paths):

        for path in paths:
            if path not in self.image_queue and path != self.displayed_img:
                self.image_queue.append(path)

        self.update_queue_display()

    def load_from_queue(self):
        if len(self.image_queue) != 0:
            next_img = self.image_queue.popleft()
            self.load_main_display(next_img)
            self.update_queue_display()
        else:
            self.clear_main_display()

    def clear_main_display(self):
        self.dnd_area.image = None
        self.update_save_path_entries("")
        self.displayed_img = None
        self.update_dnd_img_infos()

    def delete_queue(self):
        self.image_queue.clear()
        self.update_queue_display()

    def update_queue_display(self):
        elem_per_row = 4
        max_rows = 6

        for elem in self.queue_frame.winfo_children():
            elem.destroy()

        for i, item in enumerate(self.image_queue):

            # New queue element:
            elem_frame = tk.Frame(self.queue_frame, width=App.img_queue_size, height=App.img_queue_size,
                                  bg=self.queue_frame.cget("bg"))
            elem_frame.grid(row=i // elem_per_row, column=elem_per_row - i % elem_per_row)
            elem_frame.pack_propagate(False)

            if i >= elem_per_row * max_rows - 1 and len(self.image_queue) > elem_per_row * max_rows:
                info_label = tk.Label(elem_frame, text=f"+{len(self.image_queue) - elem_per_row * max_rows + 1}",
                                      bg=App.cols["dnd_border_base"], font=Font(size=10, weight="bold"))
                info_label.pack(padx=1, pady=1, anchor="center", fill="both", expand=True)
                break

            if item not in self.queue_tk_img_obj.keys():
                tk_img = ImageTk.PhotoImage(load_img(item, set_size=App.img_queue_size - 2))
                self.queue_tk_img_obj[item] = tk_img

            img_label = tk.Label(elem_frame, image=self.queue_tk_img_obj[item], bg=App.cols["dnd_border_base"])
            img_label.pack(padx=1, pady=1, anchor="center", fill="both", expand=True)

        if len(self.image_queue) != 0:

            delete_button = BorderBtn(self.queue_frame, text="Clear Queue", command=self.delete_queue,
                                      palette=BtnPalette.red_light(), border_width=1)
            delete_button.grid(row=max_rows+1, column=1, columnspan=elem_per_row, sticky="ew", padx=1, pady=1)


if __name__ == '__main__':
    app = App()
    app.mainloop()
