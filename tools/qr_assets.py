# QR 코드 + 영상용 QR 엔딩 화면(1920x1080) + 모서리 QR 배지(투명 배경) 만들기
# 사용 예)
#   python qr_assets.py --url https://example.com --out ../2026-11-sansa \
#       --title "마음의 평화를" --sub "지금 산사의 마음에 들어와 보세요"
# 만든 QR 은 OpenCV 로 다시 읽어 주소가 맞는지 확인한다.
import argparse
import base64
from pathlib import Path

import cv2
import segno
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--url", required=True, help="QR 이 가리킬 주소 (https:// 포함)")
ap.add_argument("--out", required=True, help="결과 폴더")
ap.add_argument("--title", default="지금 바로 들어와 보세요")
ap.add_argument("--sub", default="")
ap.add_argument("--label", default="사이트 바로가기", help="모서리 배지 문구")
ap.add_argument("--theme", default="sansa", choices=["sansa", "modern"], help="sansa=한지·붓글씨, modern=남색·고딕")
ap.add_argument("--icon", default="心", help="엔딩 화면 아이콘 글자/이모지")
a = ap.parse_args()

out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
qr_path = out / "qr.png"
segno.make(a.url, error="h").save(str(qr_path), scale=20, border=3, dark="#2b2621", light="#ffffff")
QR = "data:image/png;base64," + base64.b64encode(qr_path.read_bytes()).decode()
short = a.url.split("://", 1)[-1].rstrip("/")

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Nanum+Brush+Script&family=Gaegu:wght@400;700&family=Noto+Sans+KR:wght@500;800;900&display=swap" rel="stylesheet">'

END = f"""<!doctype html><html><head><meta charset="utf-8">{FONTS}</head><body style="margin:0">
<div style="width:1920px;height:1080px;display:flex;align-items:center;justify-content:center;gap:120px;
  background:radial-gradient(ellipse at 50% 40%,#fbf4e4,#ecdfc4 70%,#dccaa6)">
  <div>
    <div style="display:inline-grid;place-items:center;width:110px;height:110px;background:#b8432f;color:#f3ead8;font-size:64px;
      border-radius:12px 16px 10px 18px;transform:rotate(-5deg);font-family:'Gowun Batang',serif">{a.icon}</div>
    <div style="font-family:'Nanum Brush Script',cursive;font-size:130px;line-height:1;color:#2b2621;margin-top:30px">{a.title}</div>
    <div style="font-family:'Gowun Batang',serif;font-size:36px;color:#5f554b;margin-top:24px">{a.sub}</div>
    <div style="font-family:'Gaegu',cursive;font-size:42px;color:#3f7a6a;margin-top:34px">{short}</div>
  </div>
  <div style="text-align:center">
    <div style="background:#fff;padding:18px;border:4px solid #2b2621;border-radius:18px;box-shadow:6px 8px 0 #2b2621">
      <img src="{QR}" style="width:420px;height:420px;display:block;image-rendering:pixelated"></div>
    <div style="font-family:'Gaegu',cursive;font-size:40px;color:#b8432f;margin-top:26px">📱 휴대폰 카메라로 비춰 보세요</div>
  </div>
</div></body></html>"""

BADGE = f"""<!doctype html><html><head><meta charset="utf-8">{FONTS}</head><body style="margin:0;background:transparent">
<div id="badge" style="display:inline-flex;align-items:center;gap:14px;padding:12px 18px 12px 12px;
  background:rgba(251,246,234,.96);border:3px solid #2b2621;border-radius:16px 10px 18px 12px;box-shadow:4px 5px 0 rgba(43,38,33,.85)">
  <img src="{QR}" style="width:150px;height:150px;display:block;image-rendering:pixelated;border-radius:6px">
  <div style="font-family:'Gaegu',cursive;color:#2b2621;line-height:1.25">
    <div style="font-size:30px;color:#b8432f">{a.label}</div>
    <div style="font-size:24px">카메라로 QR을<br>비춰 보세요</div>
  </div>
</div></body></html>"""

if a.theme == "modern":
    for old, new in [("radial-gradient(ellipse at 50% 40%,#fbf4e4,#ecdfc4 70%,#dccaa6)", "radial-gradient(ellipse at 50% 35%,#2563eb,#1e3a8a 60%,#0f172a)"),
                     ("'Nanum Brush Script',cursive;font-size:130px", "'Noto Sans KR',sans-serif;font-weight:900;font-size:110px"),
                     ("color:#2b2621;margin-top:30px", "color:#ffffff;margin-top:30px"),
                     ("'Gowun Batang',serif;font-size:36px;color:#5f554b", "'Noto Sans KR',sans-serif;font-size:36px;color:#dbeafe"),
                     ("'Gaegu',cursive;font-size:42px;color:#3f7a6a", "'Noto Sans KR',sans-serif;font-weight:800;font-size:36px;color:#fde047"),
                     ("'Gaegu',cursive;font-size:40px;color:#b8432f", "'Noto Sans KR',sans-serif;font-weight:800;font-size:34px;color:#fde047"),
                     ("background:#b8432f;color:#f3ead8;font-size:64px", "background:#ffffff;color:#1e3a8a;font-size:64px"),
                     ("border:4px solid #2b2621;border-radius:18px;box-shadow:6px 8px 0 #2b2621", "border:4px solid #0f172a;border-radius:18px;box-shadow:0 12px 30px rgba(0,0,0,.4)")]:
        END = END.replace(old, new)
    for old, new in [("'Gaegu',cursive;color:#2b2621", "'Noto Sans KR',sans-serif;font-weight:800;color:#0f172a"),
                     ("color:#b8432f\">", "color:#1d4ed8\">"),
                     ("background:rgba(251,246,234,.96);border:3px solid #2b2621", "background:rgba(255,255,255,.96);border:3px solid #1e3a8a")]:
        BADGE = BADGE.replace(old, new)

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.set_content(END, wait_until="networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
    pg.screenshot(path=str(out / "end_qr.png"))
    pg.set_content(BADGE, wait_until="networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
    pg.locator("#badge").screenshot(path=str(out / "badge.png"), omit_background=True)
    b.close()

det = cv2.QRCodeDetector()
for f in ["qr.png", "end_qr.png", "badge.png"]:
    got = det.detectAndDecode(cv2.imread(str(out / f)))[0]
    print(f"{f}: {'OK' if got == a.url else 'FAIL'} ({got})")
