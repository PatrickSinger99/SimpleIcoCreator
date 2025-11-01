import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
from utils.image_edit import *
from datetime import datetime
from pathlib import Path
import os

st.set_page_config(page_title="Ico Generator", layout="wide")
ss = st.session_state


def init_session_states():
    defaults = {
        "queue": [],
        "selected_index": None,
        "cropped_img": None,
        "working_img": None,
        "processed_hashes": set(),  # track which files are already in the queue
        "go_to_next_img": True,
        "selected_border": False
    }

    for key, value in defaults.items():
        if key not in ss:
            ss[key] = value


def populate_queue():
    uploaded_files = ss.get("uploaded_files", [])
    added_count = 0

    if not uploaded_files:
        return

    for f in uploaded_files:
        h = file_hash(f)
        if h not in ss["processed_hashes"]:
            pil_img = Image.open(f).convert("RGB")
            ss["queue"].append({
                "name": f.name,
                "file": f,
                "pil": pil_img,
                "thumb": resize_with_fill(pil_img, (128, 128)),
                "hash": h
            })
            ss["processed_hashes"].add(h)
            added_count += 1


def select_queue_image(index: int = 0, overwrite: bool = True):
    # Only reset if we're actually changing the selected image
    if not overwrite and ss["selected_index"] is not None:
        return

    if len(ss["queue"]) > index:
        ss["selected_index"] = index
        # Reset cropped/working image because selection changed
        ss["cropped_img"] = None
        ss["working_img"] = None
    else:
        ss["selected_index"] = None
        ss["cropped_img"] = None
        ss["working_img"] = None


def on_crop_change(func):
    """
    Decorator to call `func` only when the crop changes.
    """
    if "prev_cropped_img" not in ss:
        ss["prev_cropped_img"] = None

    current = ss.get("cropped_img")
    prev = ss.get("prev_cropped_img")

    # Compare images by bytes
    if current is not None:
        buf = io.BytesIO()
        current.save(buf, format="PNG")
        current_bytes = buf.getvalue()
    else:
        current_bytes = None

    if prev is not None:
        buf = io.BytesIO()
        prev.save(buf, format="PNG")
        prev_bytes = buf.getvalue()
    else:
        prev_bytes = None

    if current_bytes != prev_bytes:
        func(current)
        # update the stored previous crop
        ss["prev_cropped_img"] = current



def upload_frame():
    with st.container(border=True):
        st.subheader("Upload Images")


        st.file_uploader("Image Upload", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True,
                         label_visibility="collapsed", key="uploaded_files")

        populate_queue()
        select_queue_image(overwrite=False)

        st.write(f"In Queue: {len(ss['queue'])}")
        display_queue()


def display_queue():
    cols = st.columns(4)

    for i, col in enumerate(cols):

        with col:
            for j, img in enumerate(ss.queue[:16]):
                if j % 4 == i:
                    st.image(img["thumb"])

    if len(ss.queue) > 16:
        st.text(f"+ {len(ss.queue) - 16} more")


def edit_frame():
    with st.container(border=True):
        st.subheader("Edit Image")

        if ss["selected_index"] is not None:
            img = ss['queue'][ss['selected_index']]

            st.write(f"Selected Image: {img['name']}")

            ss["cropped_img"] = st_cropper(img["pil"], realtime_update=True, box_color='#FF4B4B', aspect_ratio=(1, 1),
                                           return_type="image")

            on_crop_change(update_working_image)

            st.checkbox("Add Border", key="selected_border")


        else:
            st.info("No image selected")


def update_working_image(cropped_img, coords=(21, 21, 225, 225)):
    if cropped_img is None:
        return

    if ss.get("selected_border"):
        border = Image.open("borders/basic_square.png").convert("RGBA")
        result = border.copy()  # start with the border

        if coords:
            x1, y1, x2, y2 = coords
            target_width = x2 - x1
            target_height = y2 - y1
            resized_img = cropped_img.convert("RGBA").resize((target_width, target_height))

            # Use alpha channel as mask
            result.paste(resized_img, (x1, y1), mask=resized_img.split()[3])

        ss["working_img"] = result
    else:
        ss["working_img"] = cropped_img.convert("RGBA").resize((256, 256))

def create_frame():

    with st.container(border=True):

        if ss["working_img"]:

            st.html(f"""<div style="width:100%; text-align:center;">
                        <img src="data:image/png;base64,{pil_to_base64(ss.working_img)}" style="width:100%; height:auto;" />
                        </div>""")

        if st.button("Save as ICO", width="stretch"):
            print(ss["working_img"])
            if ss["working_img"]:
                save_as_ico(ss["working_img"], ss['queue'][ss['selected_index']]["name"])

            if ss.go_to_next_img:
                ss["queue"].pop(ss["selected_index"])
                select_queue_image()
                st.rerun()

        st.checkbox("Go to next image", key="go_to_next_img")


def save_as_ico(pil_img, original_name="image", download_folder=None):
    """
    Save a PIL image as an ICO file including multiple sizes up to 256x256.
    The file is saved in the user's Downloads folder with a name based on
    the first 12 letters of `original_name` and the current datetime.

    pil_img: PIL.Image object (RGBA)
    original_name: str, name of the original file
    download_folder: optional path to folder (defaults to system Downloads)
    """
    # Ensure image is RGBA
    pil_img = pil_img.convert("RGBA")

    # Determine Downloads folder
    if download_folder is None:
        download_folder = str(Path.home() / "Downloads")

    # Sanitize original_name and take first 12 letters
    base_name = "".join(c for c in original_name if c.isalnum())[:12]

    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{base_name}_{timestamp}.ico"
    path = os.path.join(download_folder, filename)

    # Standard icon sizes
    sizes = [16, 32, 48, 64, 128, 256]

    # Save as ICO with multiple sizes
    pil_img.save(path, format="ICO", sizes=[(s, s) for s in sizes])

    return path


def main():
    init_session_states()

    left_col, mid_col, right_col = st.columns((.25, .5, .25))

    with left_col:
        upload_frame()

    with mid_col:
        edit_frame()

    with right_col:
        create_frame()


if __name__ == '__main__':
    main()
