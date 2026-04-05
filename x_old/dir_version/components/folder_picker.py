import tkinter as tk
from tkinter import filedialog
import tempfile
import os
import time


root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

folder = filedialog.askdirectory()

# Write result to temp file
if folder:
    temp_file = os.path.join(tempfile.gettempdir(), "ico_creator_selected_dir.txt")

    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(folder)

root.destroy()
