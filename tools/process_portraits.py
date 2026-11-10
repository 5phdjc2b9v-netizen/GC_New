from pathlib import Path
from shutil import copyfile

Path("assets/images/team").mkdir(parents=True, exist_ok=True)

# The final portraits are supplied already cut out and composition-matched.
# Do not run background removal, cropping, scaling or any other image processing.
copyfile("/tmp/anja.png", "assets/images/team/anja-alexandra-pfister.png")
copyfile("/tmp/klaus.png", "assets/images/team/dr-klaus-hoehne.png")

page = Path("unternehmen.html")
s = page.read_text()
for old in (
    "./assets/images/team/anja-alexandra-pfister.webp",
    "https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/IMG_5727.JPG",
):
    s = s.replace(old, "./assets/images/team/anja-alexandra-pfister.png")
for old in (
    "./assets/images/team/dr-klaus-hoehne.webp",
    "./assets/images/team/dr-klaus-hoehne.jpg",
    "https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/PHOTO-2026-10-17-00-04-16.jpg",
):
    s = s.replace(old, "./assets/images/team/dr-klaus-hoehne.png")
page.write_text(s)
