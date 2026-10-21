import os
import zipfile
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "J-Stars Victory+ PC Version")
OUT_DIR = os.path.join(ROOT_DIR, "out")
ZIP_PATH = os.path.join(OUT_DIR, "J-Stars-Victory-VS-PC-portable-windows.zip")

os.makedirs(OUT_DIR, exist_ok=True)

if os.path.exists(ZIP_PATH):
    print(f"Removing old zip: {ZIP_PATH}")
    os.remove(ZIP_PATH)

print(f"Creating portable zip: {ZIP_PATH}")

with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
    # 1. Add specific root files and all DLLs
    for item in os.listdir(SRC_DIR):
        src_item = os.path.join(SRC_DIR, item)
        if os.path.isfile(src_item):
            ext = os.path.splitext(item)[1].lower()
            name = item.lower()
            
            # Skip logs and test artifacts
            if ext in ['.log', '.err', '.tmp']:
                continue
                
            # Include executables, batch files, text docs, icons, and DLLs
            if ext in ['.exe', '.bat', '.txt', '.ico', '.dll', '.lnk']:
                print(f"Adding root file: {item}")
                zipf.write(src_item, arcname=item)
                
    # 2. Add empty extracted_game/app0/ with PUT_GAME_FILES_HERE.txt
    readme_content = """J-Stars Victory VS+ PC - Game Data Directory
===================================================

Extract your legitimate PS4 game dump (Title ID: CUSA01887 / CUSA01593) here:

extracted_game/app0/
├── eboot.bin
├── sce_module/
│   ├── libc.prx
│   └── libSceFios2.prx
├── sce_sys/
│   ├── icon0.png
│   ├── pic0.png
│   └── param.sfo
└── data/ (or .cpk archives)

After placing the game files here, launch Launcher.exe to play!
"""
    zipf.writestr("extracted_game/app0/PUT_GAME_FILES_HERE.txt", readme_content)
    print("Added extracted_game/app0/PUT_GAME_FILES_HERE.txt")

size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
print(f"Successfully created: {ZIP_PATH} ({size_mb:.2f} MB)")
