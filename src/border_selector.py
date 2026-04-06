import tkinter as tk
from PIL import Image, ImageTk
import os
from dataclasses import dataclass
import json
from typing import Optional
from utils import resource_path

@dataclass
class BorderItem:
    item_name: str | None
    display_name: str
    img_x1: int
    img_y1: int
    img_x2: int
    img_y2: int
    border_img: Optional[Image] = None
    tk_sample_obj: Optional[ImageTk.PhotoImage] = None


class BorderSelector(tk.Frame):
    item_size = 80
    item_border_weight = 8
    selected_color = "#FF8411"
    content_path = resource_path(r".\static\borders")

    def __init__(self, *args, on_selection_change=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.on_selection_change = on_selection_change
        self.currently_selected = None

        self.selector_frame = tk.Frame(self)
        self.selector_frame.pack(side="left")

        self.borders = [f for f in os.listdir(BorderSelector.content_path) if os.path.isdir(os.path.join(BorderSelector.content_path, f))]
        print(f"Found {len(self.borders)} borders")

        # Init borders
        self.border_items = {None: self.no_border_item()}
        for border in self.borders:
            self.border_items[border] = self.init_item(border)

        # Draw borders
        for name, item in self.border_items.items():
            item_frame = self.draw_item(item)
            item_frame.pack(side="left")

    def init_item(self, border_folder):

        # Read data file and original image
        border_path = os.path.join(BorderSelector.content_path, border_folder)
        with open(os.path.join(border_path, "data.json"), "r", encoding="utf-8") as file:
            data = json.load(file)
        border_img_pil = Image.open(os.path.join(border_path, "img.png"))

        # Create new border obj
        item_obj = BorderItem(item_name=border_folder, display_name=data["name"],
                              border_img=border_img_pil, img_x1=data["img_x1"], img_x2=data["img_x2"],
                              img_y1=data["img_y1"], img_y2=data["img_y2"])

        # Create the sample image for display
        sample_img = Image.open(os.path.join(BorderSelector.content_path, "sample.jpg"))
        preview_img = add_border(sample_img, item_obj)
        resized_preview = preview_img.resize((BorderSelector.item_size, BorderSelector.item_size), Image.LANCZOS)
        item_obj.tk_sample_obj = ImageTk.PhotoImage(resized_preview)

        return item_obj

    def draw_item(self, border_item: BorderItem):
        border_col = BorderSelector.selected_color if border_item.item_name == self.currently_selected else ""
        item_frame = tk.Frame(self.selector_frame, bg=border_col)
        border_frame = tk.Frame(item_frame)
        border_frame.pack(padx=BorderSelector.item_border_weight, pady=BorderSelector.item_border_weight)
        
        label = tk.Label(border_frame, image=border_item.tk_sample_obj, bd=0, cursor="hand2")
        label.pack()
        
        # Bind click handler
        label.bind("<Button-1>", lambda e: self.on_selection(border_item.item_name))

        return item_frame

    @staticmethod
    def no_border_item():

        sample_img = Image.open(os.path.join(BorderSelector.content_path, "sample.jpg"))
        resized_preview = sample_img.resize((BorderSelector.item_size, BorderSelector.item_size), Image.LANCZOS)
        no_border_preview = ImageTk.PhotoImage(resized_preview)

        item = BorderItem(item_name=None, display_name="No Border", tk_sample_obj=no_border_preview, img_x1=0, img_y1=0,
                          img_x2=BorderSelector.item_size, img_y2=BorderSelector.item_size)

        return item

    def on_selection(self, border_name):
        if self.currently_selected == border_name:
            return  # No change needed
            
        self.currently_selected = border_name
        
        # Redraw all items
        for widget in self.selector_frame.winfo_children():
            widget.destroy()
            
        for name, item in self.border_items.items():
            item_frame = self.draw_item(item)
            item_frame.pack(side="left")
        
        # Notify parent of selection change
        if self.on_selection_change:
            self.on_selection_change(border_name)
        

def add_border(pil_img: Image, item: BorderItem):

    composed_img = item.border_img.copy()

    # Calculate and convert orig img to scale
    target_width = item.img_x2 - item.img_x1
    target_height = item.img_y2 - item.img_y1
    resized_img = pil_img.convert("RGBA").resize((target_width, target_height))

    # Use alpha channel as mask
    composed_img.paste(resized_img, (item.img_x1, item.img_y1), mask=resized_img.split()[3])

    return composed_img
