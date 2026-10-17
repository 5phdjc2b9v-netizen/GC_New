from pathlib import Path
from PIL import Image
from rembg import remove

OUT_W, OUT_H = 1200, 1500
MAX_W, MAX_H = 1120, 1430

def process(src, dst):
    im = Image.open(src).convert("RGBA")
    cut = remove(
        im,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=8,
    )
    alpha = cut.getchannel("A")
    bbox = alpha.getbbox()
    if bbox:
        cut = cut.crop(bbox)
    scale = min(MAX_W / cut.width, MAX_H / cut.height)
    size = (max(1, round(cut.width * scale)), max(1, round(cut.height * scale)))
    cut = cut.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    x = (OUT_W - cut.width) // 2
    y = OUT_H - cut.height - 18
    canvas.alpha_composite(cut, (x, y))
    canvas.save(dst, "WEBP", lossless=True, method=6)

Path("assets/images/team").mkdir(parents=True, exist_ok=True)
process("/tmp/anja.jpg", "assets/images/team/anja-alexandra-pfister.webp")
process("/tmp/klaus.jpg", "assets/images/team/dr-klaus-hoehne.webp")

page = Path("unternehmen.html")
s = page.read_text()
s = s.replace(
    "https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/IMG_5727.JPG",
    "./assets/images/team/anja-alexandra-pfister.webp",
)
s = s.replace(
    "https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/PHOTO-2026-10-17-00-04-16.jpg",
    "./assets/images/team/dr-klaus-hoehne.webp",
)
page.write_text(s)

css = Path("assets/css/styles.css")
c = css.read_text()
marker = "/* Leadership portraits: transparent, equal scale */"
if marker not in c:
    c += r"""

/* Leadership portraits: transparent, equal scale */
.portrait-cutout{
  min-height:530px;
  align-items:flex-end;
}
.portrait-cutout img,
.leader-portrait-klaus .portrait-cutout img{
  width:min(100%,440px);
  height:520px;
  object-fit:contain;
  object-position:center bottom;
  -webkit-mask-image:none;
  mask-image:none;
  filter:drop-shadow(0 18px 22px rgba(23,23,23,.12));
}
.leader-portrait-anja,
.leader-portrait-klaus{
  transform:none;
}
@media(max-width:900px){
  .portrait-cutout{min-height:430px}
  .portrait-cutout img,
  .leader-portrait-klaus .portrait-cutout img{
    width:min(100%,380px);
    height:420px;
  }
}
@media(max-width:640px){
  .portrait-cutout{min-height:370px}
  .portrait-cutout img,
  .leader-portrait-klaus .portrait-cutout img{
    width:min(100%,340px);
    height:360px;
  }
}
"""
css.write_text(c)
