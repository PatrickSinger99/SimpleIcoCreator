from PIL import IcoImagePlugin, Image

icon = Image.open(r"./imgs/icon_edited.ico")


# Get the list of available sizes from the .ico file metadata
sizes = icon.info.get('sizes', [])

if sizes:
    print("Sizes embedded in .ico file:")
    for size in sizes:
        print(size)
else:
    print("Only one size available:", icon.size)
