import streamlit as st
import tempfile
import os
import subprocess


ss = st.session_state

TEMP_FILE = os.path.join(tempfile.gettempdir(), "ico_creator_selected_dir.txt")


def directory_selector():

    def verify_dir():
        print(ss.dir_select_entry_widget)

    def pick_folder():
        # Remove old file
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)

        # Launch external script
        subprocess.run(["python", "./dir_version/components/folder_picker.py"])

        # Read new dir
        if os.path.exists(TEMP_FILE):
            with open(TEMP_FILE, "r", encoding="utf-8") as f:
                new_dir = f.read().strip()

            ss.dir_select_entry_widget = new_dir

    with st.container(border=True, horizontal=True):

        st.button("Select Folder", on_click=pick_folder)

        st.text_input(label="dir_select_entry_widget_label", key="dir_select_entry_widget", on_change=verify_dir,
                      width="stretch", label_visibility="collapsed")

