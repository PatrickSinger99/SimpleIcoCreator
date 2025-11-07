import os
import ctypes
from PIL import Image
from typing import Optional, List


def convert_to_ico(pil_obj, output_path, sizes: Optional[List[int]] = None):

    max_size = 256  # Max size that windows supports

    if sizes is not None:
        dim_sizes = [(s, s) for s in sizes]
    else:  # Pick Common sizes
        dim_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    try:
        # Open and resize image
        img = pil_obj
        img.thumbnail((max_size, max_size), Image.LANCZOS)  # Keeps aspect ratio
        width, height = img.size

        if width == height:  # Square src image
            transparent_img = img.convert('RGBA')
        elif width > height:
            transparent_img = Image.new('RGBA', (max_size, max_size), (255, 0, 0, 0))
            transparent_img.paste(img, (0, int((width-height)/2)))
        else:
            transparent_img = Image.new('RGBA', (max_size, max_size), (255, 0, 0, 0))
            transparent_img.paste(img, (int((height-width)/2), 0))

        transparent_img.save(output_path, sizes=dim_sizes)  # Outpath variable is expected to have ".ico"
        print("Created ICO file with sizes:", dim_sizes)

    except Exception as e:
        print("Error when saving as ICO:", e)


def set_folder_icon(folder_path, icon_path):
    desktop_ini = os.path.join(folder_path, "desktop.ini")

    # Remove desktop.ini if already there
    if os.path.exists(desktop_ini):
        os.remove(desktop_ini)

    # Write the configuration to the desktop.ini file
    with open(desktop_ini, "w") as f:
        f.write(f"[.ShellClassInfo]\n"
                f"IconResource={icon_path},0\n"
                f"IconFile=%SystemRoot%\\system32\\SHELL32.dll\n"
                f"IconIndex=0\n")

    # Set the desktop.ini file as hidden and system
    ctypes.windll.kernel32.SetFileAttributesW(desktop_ini, 6)

    # Set the folder as read-only
    ctypes.windll.kernel32.SetFileAttributesW(folder_path, 1)


def load_img(path, set_size: Optional[int]):
    image = Image.open(path)

    if set_size:
        width, height = image.size
        if height >= width:
            new_width, new_height = round((width / height) * set_size), set_size
        else:
            new_width, new_height = set_size, round((height / width) * set_size)
        image = image.resize((new_width, new_height))

    return image


def create_checkerboard_pattern(width, height, square_size=10, color1=(225, 225, 225), color2=(255, 255, 255)):

    img = Image.new("RGB", (width, height), color1)
    for y in range(0, height, square_size):
        for x in range(0, width, square_size):
            if (x // square_size + y // square_size) % 2 == 0:
                for i in range(square_size):
                    for j in range(square_size):
                        if x + i < width and y + j < height:
                            img.putpixel((x + i, y + j), color2)

    return img