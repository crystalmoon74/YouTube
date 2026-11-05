# Everyday AI Works — 유튜브 프로필(800x800)과 배너(2560x1440) 이미지 만들기
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "channel"
OUT.mkdir(parents=True, exist_ok=True)

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700;9..144,900&family=Gaegu:wght@700&family=Gowun+Dodum&display=swap" rel="stylesheet">'
INK, PAPER, CORAL, TEAL, SUN = "#1f2430", "#f6f1e7", "#e8553d", "#2a8c82", "#f2c14e"

SPARK = f'<path d="M0 -50 C 6 -14 14 -6 50 0 C 14 6 6 14 0 50 C -6 14 -14 6 -50 0 C -14 -6 -6 -14 0 -50Z" fill="{SUN}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'

PROFILE = f"""<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>
html,body{{margin:0;width:800px;height:800px;background:{INK};overflow:hidden}}
.wrap{{position:relative;width:800px;height:800px;display:grid;place-items:center;
  background:radial-gradient(circle at 50% 42%,#2c3346,{INK} 70%)}}
.ai{{font-family:'Fraunces',serif;font-weight:900;font-size:390px;line-height:1;color:{PAPER};letter-spacing:-12px;
  transform:translateY(-14px)}}
.ai i{{font-style:normal;color:{PAPER}}}
.bar{{position:absolute;left:220px;top:560px;width:360px;height:26px;border-radius:13px;background:{CORAL};transform:rotate(-2deg)}}
.sp{{position:absolute;left:555px;top:150px}}
.dot{{position:absolute;width:30px;height:30px;border-radius:50%;background:{TEAL};left:205px;top:205px}}
.ring{{position:absolute;inset:26px;border-radius:50%;border:10px dashed rgba(246,241,231,.18)}}
</style></head><body><div class="wrap">
<div class="ring"></div>
<div class="ai">AI</div>
<div class="bar"></div>
<svg class="sp" width="130" height="130" viewBox="-65 -65 130 130">{SPARK}</svg>
</div></body></html>"""

DOODLES = f"""
<svg width="2560" height="1440" viewBox="0 0 2560 1440" style="position:absolute;inset:0" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
  <!-- 왼쪽: 브라우저 창 -->
  <g transform="translate(110 560) rotate(-6)">
    <rect x="0" y="0" width="300" height="220" rx="18" fill="#fff"/>
    <path d="M0 50 H300"/><circle cx="28" cy="25" r="7" fill="{CORAL}"/><circle cx="52" cy="25" r="7" fill="{SUN}"/><circle cx="76" cy="25" r="7" fill="{TEAL}"/>
    <path d="M40 95 H200 M40 135 H250 M40 175 H160" stroke-width="10" stroke="{TEAL}" opacity=".7"/>
  </g>
  <!-- 왼쪽 아래: 코드 괄호 -->
  <g transform="translate(330 800) scale(.8)"><path d="M60 0 L0 60 L60 120" stroke="{CORAL}" stroke-width="16"/><path d="M110 0 L170 60 L110 120" stroke="{CORAL}" stroke-width="16"/></g>
  <!-- 오른쪽: 필름(영상) -->
  <g transform="translate(2150 545) rotate(7)">
    <rect x="0" y="0" width="280" height="200" rx="16" fill="{INK}"/>
    <path d="M0 40 H280 M0 160 H280" stroke="{PAPER}" stroke-width="4"/>
    <g fill="{PAPER}" stroke="none">{''.join(f'<rect x="{18+i*50}" y="12" width="22" height="16" rx="3"/><rect x="{18+i*50}" y="172" width="22" height="16" rx="3"/>' for i in range(6))}</g>
    <path d="M120 70 L175 100 L120 130Z" fill="{SUN}" stroke="none"/>
  </g>
  <!-- 오른쪽 아래: 톱니(자동화) -->
  <g transform="translate(2160 850) scale(.8)">
    <circle r="70" fill="{SUN}"/><circle r="26" fill="{PAPER}"/>
    {''.join(f'<rect x="-14" y="-98" width="28" height="34" rx="6" fill="{SUN}" transform="rotate({a})"/>' for a in range(0,360,45))}
  </g>
  <!-- 반짝이 -->
  <g transform="translate(470 610) scale(.55)">{SPARK}</g>
  <g transform="translate(2420 820) scale(.6)">{SPARK}</g>
  <!-- 손글씨 화살표 -->
  <path d="M60 880 C 110 920 170 920 210 880" stroke="{TEAL}" stroke-width="7"/><path d="M195 857 L212 880 L182 890" stroke="{TEAL}" stroke-width="7"/>
</svg>"""

BANNER = f"""<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>
html,body{{margin:0;width:2560px;height:1440px;overflow:hidden}}
.bg{{position:relative;width:2560px;height:1440px;background-color:{PAPER};
  background-image:linear-gradient(rgba(31,36,48,.06) 2px,transparent 2px),linear-gradient(90deg,rgba(31,36,48,.06) 2px,transparent 2px);
  background-size:64px 64px}}
.safe{{position:absolute;left:507px;top:509px;width:1546px;height:423px;display:flex;align-items:center;justify-content:center;gap:56px}}
.logo{{flex:none;width:250px;height:250px;border-radius:50%;background:{INK};display:grid;place-items:center;position:relative;
  box-shadow:10px 12px 0 {CORAL}}}
.logo span{{font-family:'Fraunces',serif;font-weight:900;font-size:130px;color:{PAPER};letter-spacing:-5px;transform:translateY(-6px)}}
.logo svg{{position:absolute;right:-6px;top:6px}}
.txt h1{{margin:0;font-family:'Fraunces',serif;font-weight:900;font-size:128px;line-height:1;color:{INK};letter-spacing:-2px;white-space:nowrap}}
.txt h1 em{{font-style:normal;color:{CORAL}}}
.txt p{{margin:22px 0 0;font-family:'Gowun Dodum',sans-serif;font-size:50px;color:{INK}}}
.txt .tags{{margin-top:22px;display:flex;gap:16px}}
.txt .tags b{{font-family:'Gowun Dodum',sans-serif;font-weight:400;font-size:34px;padding:6px 24px;border:4px solid {INK};border-radius:30px 18px 32px 16px;background:#fff}}
</style></head><body><div class="bg">
{DOODLES}
<div class="safe">
  <div class="logo"><span>AI</span><svg width="80" height="80" viewBox="-65 -65 130 130">{SPARK}</svg></div>
  <div class="txt">
    <h1>Everyday <em>AI</em> Works</h1>
    <p>매일, AI와 함께 만드는 작은 작품들</p>
    <div class="tags"><b>웹사이트</b><b>앱</b><b>영상</b><b>자동화</b></div>
  </div>
</div>
</div></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    for name, html, w, h in [("profile", PROFILE, 800, 800), ("banner", BANNER, 2560, 1440)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.set_content(html, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(OUT / f"{name}.png"))
        pg.close()
    b.close()
print("ok")
