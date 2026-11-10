from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(".")
ABOUT=ROOT/"assets/images/about"
PARTNERS=ROOT/"assets/images/partners"
TEAM=ROOT/"assets/images/team"
TRADE=ROOT/"assets/images/trade"

def trim_alpha(path, pad=8):
    p=Path(path)
    im=Image.open(p).convert("RGBA")
    a=im.getchannel("A")
    bbox=a.point(lambda v: 255 if v>8 else 0).getbbox()
    if bbox:
        l,t,r,b=bbox
        l=max(0,l-pad); t=max(0,t-pad); r=min(im.width,r+pad); b=min(im.height,b+pad)
        im=im.crop((l,t,r,b))
    im.save(p)



def clean_klaus_artifacts(path):
    p=Path(path)
    im=Image.open(p).convert("RGBA")
    w,h=im.size
    px=im.load()
    # Corrupted colour bands live only in the upper-right source canvas.
    # Preserve the jacket/shoulder in the lower-right area.
    for y in range(int(h*.68)):
        for x in range(int(w*.73), w):
            r,g,b,a=px[x,y]
            # Remove the entire non-portrait side zone; the face/hair ends before it.
            px[x,y]=(r,g,b,0)
    im.save(p)
    trim_alpha(p, 8)

def keep_largest_alpha_component(path, pad=8):
    p=Path(path)
    im=Image.open(p).convert("RGBA")
    w,h=im.size
    alpha=im.getchannel("A")
    # Remove a thin corrupted strip at the very bottom before component analysis.
    ap=alpha.load()
    for y in range(max(0,h-int(h*.018)), h):
        for x in range(w):
            ap[x,y]=0

    mask=alpha.point(lambda v: 255 if v>18 else 0)
    pix=mask.load()
    seen=bytearray(w*h)
    best=[]
    from collections import deque
    for y in range(h):
        for x in range(w):
            idx=y*w+x
            if seen[idx] or pix[x,y]==0:
                continue
            q=deque([(x,y)])
            seen[idx]=1
            comp=[]
            while q:
                cx,cy=q.popleft()
                comp.append((cx,cy))
                for ny in (cy-1,cy,cy+1):
                    if ny<0 or ny>=h: continue
                    for nx in (cx-1,cx,cx+1):
                        if nx<0 or nx>=w or (nx==cx and ny==cy): continue
                        nidx=ny*w+nx
                        if not seen[nidx] and pix[nx,ny]:
                            seen[nidx]=1
                            q.append((nx,ny))
            if len(comp)>len(best):
                best=comp
    if not best:
        return
    keep=Image.new("L",(w,h),0)
    kp=keep.load()
    orig=im.getchannel("A").load()
    for x,y in best:
        kp[x,y]=orig[x,y]
    im.putalpha(keep)
    bbox=keep.getbbox()
    if bbox:
        l,t,r,b=bbox
        l=max(0,l-pad); t=max(0,t-pad); r=min(w,r+pad); b=min(h,b+pad)
        im=im.crop((l,t,r,b))
    im.save(p)

def trim_white(path, pad=10):
    p=Path(path)
    im=Image.open(p).convert("RGBA")
    # Ignore transparent and near-white source padding, but keep light logo pixels.
    px=im.load()
    mask=Image.new("L", im.size, 0)
    mp=mask.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=px[x,y]
            if a>12 and (min(r,g,b)<238 or max(r,g,b)-min(r,g,b)>14):
                mp[x,y]=255
    bbox=mask.getbbox() or im.getchannel("A").getbbox()
    if bbox:
        l,t,r,b=bbox
        l=max(0,l-pad); t=max(0,t-pad); r=min(im.width,r+pad); b=min(im.height,b+pad)
        im=im.crop((l,t,r,b))
    im.save(p)

for p in [
    ABOUT/"frankfurt-book-fair-aap.png",
    TEAM/"anja-alexandra-pfister.png",
]:
    trim_alpha(p, 8)

clean_klaus_artifacts(TEAM/"dr-klaus-hoehne.webp")

for p in PARTNERS.glob("*.png"):
    trim_white(p, 12)

# The gestalten source contains a tiny stray mark above the actual wordmark.
# Keep only the main wordmark, then trim again.
gestalten = PARTNERS/"gestalten.png"
im = Image.open(gestalten).convert("RGBA")
w,h = im.size
im = im.crop((max(0,int(w*.06)), int(h*.36), w, h))
im.save(gestalten)
trim_white(gestalten, 8)

# Replace external image dependencies with local assets.
index=Path("index.html")
s=index.read_text()
s=s.replace(
    "https://static.wixstatic.com/media/3b5c40_4f5edce81fa64bc980f3bab1eb5d72ec~mv2.jpg",
    "./assets/images/trade/boutique-coffee-table.jpg"
)
index.write_text(s)

about=Path("unternehmen.html")
s=about.read_text()
repls={
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/2026-10-FBM_AAP_TR.png":"./assets/images/about/frankfurt-book-fair-aap.png",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/IMG_8598.JPG":"./assets/images/about/frankfurt-book-fair-exterior.jpg",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/AAP_Portrait.png":"./assets/images/team/anja-alexandra-pfister.png",
"https://svgsilh.com/svg/2718284.svg":"./assets/images/about/germany-silhouette.svg",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/bikeline.png":"./assets/images/partners/bikeline.png",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/hikeline.png":"./assets/images/partners/hikeline.png",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/womo.png":"./assets/images/partners/womo.png",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/teneues.png":"./assets/images/partners/teneues.png",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/gestalten%20schwarz.png":"./assets/images/partners/gestalten.png",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/iwanowski.png":"./assets/images/partners/iwanowski.png",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/vista%20point.png":"./assets/images/partners/vista-point.png",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/teampuzzle-logo-full-color-cmyk.png":"./assets/images/partners/teampuzzle.png",
"https://raw.githubusercontent.com/5phdjc2b9v-netizen/GC_New/main/LOGO_BnA_300.png":"./assets/images/partners/book-n-app.png",
}
for old,new in repls.items():
    s=s.replace(old,new)
about.write_text(s)
