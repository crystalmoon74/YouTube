# 유튜브 썸네일(1280x720): 왼쪽 사진 + 오른쪽 제목 (산사의 마음 썸네일과 같은 구성)
# 사용 예)
#   python thumbnail.py --image https://.../photo.jpg --out ../2026-11-sansa/thumbnail.jpg \
#       --kicker "온라인 산사" --title "산사의 마음" \
#       --line1 "집에서 하는 <r>템플스테이</r>" --line2 "자녀 합격 <g>소원 기원</g>" --foot "큰절 · 범종 · 소원 편지까지"
# --image 는 인터넷 주소 또는 로컬 파일 경로. <r>…</r> 은 주홍, <g>…</g> 는 청록 강조.
import argparse
import base64
import mimetypes
from pathlib import Path

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--image", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--kicker", default="")
ap.add_argument("--title", required=True)
ap.add_argument("--line1", default="")
ap.add_argument("--line2", default="")
ap.add_argument("--foot", default="")
ap.add_argument("--pos", default="62% 22%", help="사진에서 보여 줄 위치 (CSS object-position)")
a = ap.parse_args()

img = a.image
if not img.startswith("http"):
    path = Path(img)
    img = f"data:{mimetypes.guess_type(path.name)[0] or 'image/jpeg'};base64," + base64.b64encode(path.read_bytes()).decode()


def color(s):
    return s.replace("<r>", '<span style="color:#b8432f">').replace("</r>", "</span>") \
            .replace("<g>", '<span style="color:#3f7a6a">').replace("</g>", "</span>")


HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Nanum+Brush+Script&family=Gaegu:wght@400;700&display=swap" rel="stylesheet"></head>
<body style="margin:0"><div style="width:1280px;height:720px;display:grid;grid-template-columns:1fr 1.05fr;
  background:radial-gradient(ellipse at 70% 40%,#fbf4e4,#ead9b6 75%,#d9c39a)">
  <div style="position:relative;overflow:hidden;border-right:6px solid #2b2621">
    <img src="{img}" referrerpolicy="no-referrer" style="width:100%;height:100%;object-fit:cover;object-position:{a.pos}"></div>
  <div style="display:flex;flex-direction:column;justify-content:center;padding:0 54px">
    <div style="display:flex;align-items:center;gap:18px">
      <span style="display:inline-grid;place-items:center;width:84px;height:84px;background:#b8432f;color:#f3ead8;font-size:50px;border-radius:10px 14px 9px 15px;transform:rotate(-5deg);font-family:'Gowun Batang',serif">心</span>
      <span style="font-family:'Gaegu',cursive;font-size:38px;color:#b8432f">{a.kicker}</span></div>
    <div style="font-family:'Nanum Brush Script',cursive;font-size:150px;line-height:.95;color:#2b2621;margin-top:18px">{a.title}</div>
    <div style="font-family:'Gowun Batang',serif;font-weight:700;font-size:44px;color:#2b2621;margin-top:22px;line-height:1.35">{color(a.line1)}<br>{color(a.line2)}</div>
    <div style="font-family:'Gaegu',cursive;font-size:34px;color:#5f554b;margin-top:22px">{a.foot}</div>
  </div></div></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.set_content(HTML, wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_function("() => [...document.images].every(i => i.complete && i.naturalWidth > 0)", timeout=20000)
    pg.wait_for_timeout(300)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pg.screenshot(path=a.out, type="jpeg", quality=92)
    b.close()
print("ok", a.out)
