import os
import ctypes
from PIL import Image
from typing import Optional


def create_ico(input_image, output_path="./icon", resize=None):
    image = Image.open(input_image).convert("RGBA")

    # Resizing
    if resize is not None:
        image = image.resize((resize, resize))

    # Save the image as an ico file
    image.save(os.path.join(output_path, os.path.basename(input_image).split(".")[0] + ".ico"))


def convert_to_ico(path, output_path):
    original_img = Image.open(path)
    width, height = original_img.size

    if width == height:  # Square src image
        transparent_img = original_img
    elif width > height:
        transparent_img = Image.new('RGBA', (width, width), (255, 0, 0, 0))
        transparent_img.paste(original_img, (0, int((width-height)/2)))
    else:
        transparent_img = Image.new('RGBA', (height, height), (255, 0, 0, 0))
        transparent_img.paste(original_img, (int((height-width)/2), 0))

    transparent_img.save(output_path)


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


def create_checkerboard_pattern(width, height, square_size=10, color1=(200, 200, 200), color2=(255, 255, 255)):

    img = Image.new("RGB", (width, height), color1)
    for y in range(0, height, square_size):
        for x in range(0, width, square_size):
            if (x // square_size + y // square_size) % 2 == 0:
                for i in range(square_size):
                    for j in range(square_size):
                        if x + i < width and y + j < height:
                            img.putpixel((x + i, y + j), color2)

    return img