from PIL import Image
from typing import Optional, List
import os
import ctypes


def convert_to_ico(pil_obj, output_path, sizes: Optional[List[int]] = None):
    """
    Convert a square RGBA PIL image into a multi-size ICO file.
    """

    if sizes is None:
        sizes = [16, 24, 32, 48, 64, 128, 256]

    dim_sizes = [(s, s) for s in sizes]

    try:
        # Ensure base image is large enough
        max_size = max(sizes)
        if pil_obj.size[0] < max_size:
            pil_obj = pil_obj.resize((max_size, max_size), Image.LANCZOS)

        # Let Pillow handle resizing for all icon sizes
        pil_obj.save(output_path, format="ICO", sizes=dim_sizes)

        print("Created ICO file with sizes:", dim_sizes)

    except Exception as e:
        print("Error when saving as ICO:", e)


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


def crop_img(pil_img, crop_xy1, crop_xy2, delta_x, delta_y, scale):
    """
    Crops a square region from pil_img.
    If the crop area exceeds image bounds, the outside area becomes transparent.
    """

    x1, y1 = crop_xy1 - delta_x, crop_xy1 - delta_y
    x2, y2 = crop_xy2 - delta_x, crop_xy2 - delta_y
    x1, y1, x2, y2 = int(x1 / scale), int(y1 / scale), int(x2 / scale), int(y2 / scale)

    img_w, img_h = pil_img.size

    # Fast path: fully inside bounds → normal crop
    if x1 >= 0 and y1 >= 0 and x2 <= img_w and y2 <= img_h:
        return pil_img.crop((x1, y1, x2, y2))

    # Slow path: need transparency
    if pil_img.mode != "RGBA":  # Ensure image has alpha channel
        pil_img = pil_img.convert("RGBA")

    width = x2 - x1
    height = y2 - y1

    # Create transparent result image
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Paste original image with offset
    paste_x = -x1
    paste_y = -y1

    result.paste(pil_img, (paste_x, paste_y))

    return result


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

    # Refresh view on explorer, to avoid old thumbs being shown
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)