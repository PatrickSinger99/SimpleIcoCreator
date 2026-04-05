from tkinter import ttk


def init_styles(style: ttk.Style):
    """Initialize all custom ttk styles using the provided Style instance."""

    # Base style to go off of
    style.theme_use("vista")

    # Custom button style
    style.configure("Primary.TButton",
                    foreground="red",
                    background="green")

    # Custom combobox
    style.configure("Action.TCombobox",
                    fieldbackground="white",
                    background="lightgrey",
                    foreground="black",
                    padding=(6, 4))

    style.map("Action.TCombobox",
              fieldbackground=[("readonly", "white")],
              background=[("readonly", "lightgrey")])

    # Custom entry
    style.configure("Action.TEntry",
                    foreground="black",
                    fieldbackground="white",
                    padding=(6, 4))
