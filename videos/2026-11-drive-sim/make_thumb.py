# 「다시 운전」 썸네일 (1280x720): 주행 화면 + 큰 제목 (사이트의 남색·노랑 색)
import base64
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

shot = Path(sys.argv[1])
img = "data:image/png;base64," + base64.b64encode(shot.read_bytes()).decode()
HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700;900&display=swap" rel="stylesheet"></head>
<body style="margin:0"><div style="position:relative;width:1280px;height:720px;overflow:hidden;background:#0f172a;font-family:'Noto Sans KR',sans-serif">
  <img src="{img}" style="position:absolute;right:-40px;top:40px;width:820px;border-radius:24px;box-shadow:0 20px 50px rgba(0,0,0,.5);transform:rotate(2deg)">
  <div style="position:absolute;inset:0;background:linear-gradient(90deg,#0f172a 38%,rgba(15,23,42,.6) 60%,rgba(15,23,42,0) 85%)"></div>
  <div style="position:absolute;left:60px;top:110px;width:640px;color:#fff">
    <div style="display:inline-block;background:#fde047;color:#0f172a;font-weight:900;font-size:34px;padding:6px 22px;border-radius:999px">장롱면허 탈출</div>
    <div style="font-weight:900;font-size:150px;line-height:1.05;margin-top:22px">다시<br>운전 🚗</div>
    <div style="font-weight:700;font-size:40px;margin-top:22px;line-height:1.35;color:#dbeafe">웹에서 하는<br><span style="color:#fde047">운전 · 주차 · 법규</span> 연습</div>
  </div>
</div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.set_content(HTML, wait_until="networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
    pg.screenshot(path=str(Path(__file__).parent / "thumbnail.jpg"), type="jpeg", quality=92)
    b.close()
print("ok")
