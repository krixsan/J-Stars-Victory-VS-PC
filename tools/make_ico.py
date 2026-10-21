from PIL import Image
import os

src = os.path.join("extracted_game", "app0", "sce_sys", "icon0.png")
if not os.path.exists(src):
    src = os.path.join("J-Stars Victory+ PC Version", "extracted_game", "app0", "sce_sys", "icon0.png")

img = Image.open(src)
print(f"Loaded source image: {src}, Size: {img.size}, Mode: {img.mode}")

for d in [os.path.join("packaging", "windows", "icons"), "assets", "J-Stars Victory+ PC Version"]:
    os.makedirs(d, exist_ok=True)

sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

dest_paths = [
    os.path.join("packaging", "windows", "icons", "jstars.ico"),
    os.path.join("assets", "jstars.ico"),
    os.path.join("assets", "icon.ico"),
    os.path.join("J-Stars Victory+ PC Version", "icon.ico")
]

for dst in dest_paths:
    img.save(dst, format="ICO", sizes=sizes)
    print(f"Saved {dst} size: {os.path.getsize(dst)} bytes")
