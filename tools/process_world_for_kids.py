from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

path = Path("assets/images/portfolio/world-for-kids-portugal.webp")
im = Image.open(path).convert("RGB")

# Flood-fill only the light background connected to the outer image edges.
# White elements inside the book cover remain untouched because they are not
# connected to the canvas background.
work = im.copy()
marker = (1, 254, 1)
for seed in [(0,0), (im.width-1,0), (0,im.height-1), (im.width-1,im.height-1)]:
    ImageDraw.floodfill(work, seed, marker, thresh=38)

pixels = work.load()
alpha = Image.new("L", im.size, 255)
ap = alpha.load()
for y in range(im.height):
    for x in range(im.width):
        if pixels[x,y] == marker:
            ap[x,y] = 0

# Slight feather avoids a white fringe while keeping the actual book sharp.
alpha = alpha.filter(ImageFilter.GaussianBlur(0.55))
rgba = im.convert("RGBA")
rgba.putalpha(alpha)

# Crop excess transparent canvas but leave a little breathing room.
bbox = alpha.getbbox()
if bbox:
    pad = 8
    l,t,r,b = bbox
    l=max(0,l-pad); t=max(0,t-pad); r=min(im.width,r+pad); b=min(im.height,b+pad)
    rgba = rgba.crop((l,t,r,b))

rgba.save(path, "WEBP", lossless=True, method=6)
