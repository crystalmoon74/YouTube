# 사이트 시연 녹화 스크립트 (산사의 마음 소개 영상에 쓴 원본)
# - 로컬 서버(SQLite 모드)를 Edge 로 열어 장면별로 조작하며 1600x900 으로 녹화한다. 결과: rec/*.webm, rec/marks.json
# - 새 영상에 쓸 때: BASE 주소, 장면 블록(# 0. ~ # 11.)의 자막 cap()/카드 card()/조작만 바꾸면 된다.
#   cap(제목, 설명) = 아래 자막 띠, card(제목, 설명, 주소) = 전체 화면 타이틀 카드, mark(이름) = 장면 시작 시각 기록
# - marks.json 의 시각은 유튜브 챕터(설명란 목차)를 만들 때 쓴다 (편집에서 자른 앞부분 초를 빼서 계산).
import json
import secrets
import sys
import time
import uuid
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "rec"
OUT.mkdir(exist_ok=True)
BASE = "http://localhost:8000"
W, H = 1600, 900
EMAIL = f"video-{uuid.uuid4().hex[:6]}@sansa.test"   # 로컬 테스트용 계정 (로컬 SQLite 에만 생김)
PASSWORD = secrets.token_urlsafe(12)   # 실행할 때마다 새로 만드는 로컬 테스트용 비밀번호
marks = []          # (초, 장면 이름) — 편집용 기록
T0 = None

OVERLAY = r"""
(() => {
  if (window.__cap) return;
  const css = document.createElement('style');
  css.textContent = `
  #vcap{position:fixed;left:50%;bottom:34px;transform:translate(-50%,20px);z-index:9999;opacity:0;
    min-width:52%;max-width:82%;padding:16px 34px 18px;text-align:center;pointer-events:none;
    background:rgba(32,26,22,.86);color:#f6ecd8;border-radius:18px 10px 20px 12px;
    box-shadow:0 8px 30px rgba(0,0,0,.35);transition:opacity .5s, transform .5s}
  #vcap.show{opacity:1;transform:translate(-50%,0)}
  #vcap b{display:block;font-family:"Nanum Brush Script",cursive;font-weight:400;font-size:46px;line-height:1.1;color:#f3cf7a}
  #vcap span{display:block;font-family:"Gowun Batang",serif;font-size:23px;margin-top:6px;line-height:1.5}
  #vcard{position:fixed;inset:0;z-index:10000;display:grid;place-items:center;text-align:center;opacity:0;pointer-events:none;
    transition:opacity .9s;background:radial-gradient(ellipse at 50% 40%,#fbf4e4,#ecdfc4 70%,#dccaa6)}
  #vcard.show{opacity:1}
  #vcard .seal{display:inline-grid;place-items:center;width:110px;height:110px;background:#b8432f;color:#f3ead8;
    font-size:64px;border-radius:12px 16px 10px 18px;transform:rotate(-5deg);margin-bottom:26px;font-family:"Gowun Batang",serif}
  #vcard h1{font-family:"Nanum Brush Script",cursive;font-weight:400;font-size:120px;margin:0;color:#2b2621;line-height:1}
  #vcard p{font-family:"Gowun Batang",serif;font-size:32px;color:#5f554b;margin:22px 0 0}
  #vcard .url{font-family:"Gaegu",cursive;font-size:38px;color:#3f7a6a;margin-top:30px}
  `;
  document.head.appendChild(css);
  const cap = document.createElement('div'); cap.id = 'vcap'; document.body.appendChild(cap);
  const card = document.createElement('div'); card.id = 'vcard'; document.body.appendChild(card);
  window.__cap = (t, s) => {
    if (!t) { cap.classList.remove('show'); return; }
    cap.innerHTML = '<b></b><span></span>';
    cap.querySelector('b').textContent = t; cap.querySelector('span').textContent = s || '';
    cap.classList.add('show');
  };
  window.__card = (h, p, url) => {
    if (!h) { card.classList.remove('show'); return; }
    card.innerHTML = '<div><div class="seal">心</div><h1></h1><p></p>' + (url ? '<div class="url"></div>' : '') + '</div>';
    card.querySelector('h1').textContent = h; card.querySelector('p').textContent = p || '';
    if (url) card.querySelector('.url').textContent = url;
    card.classList.add('show');
  };
})();
"""


def mark(name):
    marks.append((round(time.time() - T0, 2), name))
    print(f"[{marks[-1][0]:6.1f}s] {name}", flush=True)


def run():
    global T0
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        ctx = browser.new_context(
            viewport={"width": W, "height": H},
            record_video_dir=str(OUT), record_video_size={"width": W, "height": H},
            locale="ko-KR",
        )
        ctx.add_init_script("localStorage.setItem('sansa.music','on');")
        page = ctx.new_page()
        T0 = time.time()

        def ov():
            page.evaluate(OVERLAY)

        def cap(t, s=""):
            ov(); page.evaluate("([t,s]) => window.__cap(t,s)", [t, s])

        def nocap():
            page.evaluate("() => window.__cap && window.__cap('')")

        def card(h, sub="", url=""):
            ov(); page.evaluate("([h,p,u]) => window.__card(h,p,u)", [h, sub, url])

        def nocard():
            page.evaluate("() => window.__card && window.__card('')")

        def scroll_to(sel, offset=90):
            page.evaluate("([s,o]) => { const e=document.querySelector(s); window.scrollTo({top: e.getBoundingClientRect().top + scrollY - o, behavior:'smooth'}); }", [sel, offset])
            page.wait_for_timeout(1100)

        def scroll_top():
            page.evaluate("() => window.scrollTo({top:0, behavior:'smooth'})")
            page.wait_for_timeout(800)

        def go(hash_):
            page.evaluate("(h) => { location.hash = h }", hash_)
            page.wait_for_timeout(900)
            page.evaluate("() => window.scrollTo(0,0)")

        def next_step(t, s=""):
            page.click("#nextBtn"); page.wait_for_timeout(300)
            cap(t, s); page.wait_for_timeout(1300)

        def slow_type(sel, text, delay=55):
            page.click(sel)
            page.type(sel, text, delay=delay)

        page.goto(BASE + "/#/")
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(600)

        # 0. 오프닝
        mark("intro")
        card("산사의 마음", "온라인 템플스테이 · 소원 기원")
        page.wait_for_timeout(4200)
        nocard(); page.wait_for_timeout(900)

        # 1. 홈
        mark("home")
        cap("잠시, 마음 내려놓고 가세요", "집에서도 만나는 산사 — 손그림으로 그린 한지 위의 절집")
        page.wait_for_timeout(3800)
        scroll_to(".how", 160)
        cap("세 걸음이면 충분합니다", "사찰 고르기 → 템플스테이 → 소원 기원")
        page.wait_for_timeout(3600)

        # 2. 사찰 선택
        mark("temples")
        go("/temples")
        cap("전국 다섯 사찰", "불국사 · 해인사 · 통도사 · 송광사 · 부석사")
        page.wait_for_timeout(2500)
        for sel in [".temple-card:nth-child(1)", ".temple-card:nth-child(2)", ".temple-card:nth-child(3)"]:
            page.hover(sel); page.wait_for_timeout(700)
        page.mouse.wheel(0, 500); page.wait_for_timeout(1300)
        page.hover(".temple-card:nth-child(5)"); page.wait_for_timeout(1300)
        cap("사찰마다 다른 풍경", "다보탑·석가탑, 장경판전, 금강계단, 우화각, 배흘림기둥까지")
        page.wait_for_timeout(3000)

        # 3. 사찰 입구 — 불국사
        mark("temple")
        go("/temple/bulguksa")
        cap("산문 앞에 서면", "사찰의 이야기와 특징을 한눈에")
        page.wait_for_timeout(3500)
        scroll_to(".dharma", 70)
        page.wait_for_timeout(500)
        cap("법당 안 부처님", "실제 사찰 부처님 사진 앞에서 두 손 모아 인사드립니다")
        page.wait_for_timeout(2500)
        scroll_to("#halfBow", 420)
        page.click("#halfBow"); page.wait_for_timeout(2200)
        scroll_to(".signboards", 260)
        cap("무엇을 하시겠어요?", "템플스테이 또는 소원 기원")
        page.wait_for_timeout(3200)

        # 4. 가입
        mark("signup")
        nocap()
        go("/signup?next=%2Ftemple%2Fbulguksa")
        cap("이메일만으로 간단 가입", "이름·전화번호 없이, 개인정보는 최소한만")
        page.wait_for_timeout(1200)
        slow_type("#authForm input[name=email]", EMAIL, 45)
        page.click("#authForm input[name=password]"); page.type("#authForm input[name=password]", PASSWORD, delay=35)
        slow_type("#authForm input[name=nickname]", "연꽃", 120)
        page.wait_for_timeout(600)
        page.click("#authForm button[type=submit]")
        page.wait_for_timeout(1800)

        # 5. 템플스테이
        mark("templestay")
        page.evaluate("() => window.scrollTo(0,0)")
        scroll_to(".signboards", 260)
        page.click("#goStay")
        page.wait_for_url("**/#/stay/*"); page.wait_for_timeout(900)
        cap("템플스테이 일곱 걸음", "입재부터 회향까지, 하루 일과를 차례로")
        page.wait_for_timeout(2400)
        # 입재
        cap("입재 — 산문에 들어서기", "오늘의 마음을 고르고 합장합니다")
        page.click("#minds .chip:nth-child(2)"); page.wait_for_timeout(900)
        page.click("#hapjang"); page.wait_for_timeout(1500)
        page.click("#note"); page.type("#note", "조용히 쉬고 싶어서 왔습니다.", delay=45)
        page.wait_for_timeout(500)
        next_step("예불 — 새벽 범종", "범종을 세 번 울려 모든 생명을 깨웁니다")  # 예불
        scroll_to(".step", 100)
        for _ in range(3):
            page.click("#bellBtn"); page.wait_for_timeout(1200)
        page.wait_for_timeout(600)
        next_step("발우공양", "네 발우를 차례로 받으며 오관게를 새깁니다")  # 발우공양
        scroll_to(".step", 100)
        for i in range(4):
            page.click(f'.bowl[data-i="{i}"]', force=True); page.wait_for_timeout(900)
        page.wait_for_timeout(1200)
        next_step("울력 — 함께 하는 수행", "마루를 닦고 발우를 씻으며 마음의 먼지도 닦아냅니다")  # 울력
        scroll_to(".step", 100)
        for phase in range(2):
            page.wait_for_timeout(700)
            box = page.locator("#dust").bounding_box()
            page.mouse.move(box["x"] + 10, box["y"] + 10); page.mouse.down()
            y = box["y"] + 8
            row = 0
            while y < box["y"] + box["height"] + 10:
                xs = [box["x"] + 5, box["x"] + box["width"] - 5]
                if row % 2: xs.reverse()
                page.mouse.move(xs[1], y, steps=14)
                y += 34; row += 1
                page.mouse.move(xs[1], y, steps=2)
            page.mouse.up()
            page.wait_for_timeout(900)
        page.wait_for_timeout(800)
        next_step("참선 — 고요히 앉기", "숨이 들고 나는 것만 바라봅니다")  # 참선
        scroll_to(".step", 100)
        page.click("#mins .chip:nth-child(1)"); page.wait_for_timeout(5200)
        page.click("#stopMed"); page.wait_for_timeout(1300)
        next_step("법문 — 부처님 말씀", "마음이 가는 경전 한 장을 펼쳐 봅니다")  # 법문
        scroll_to(".step", 100)
        page.click(".sutra:nth-child(2)"); page.wait_for_timeout(3000)
        next_step("회향", "오늘의 수행을 돌아보고, 좋은 기운을 모두에게 돌려 보냅니다")  # 회향
        scroll_to("#reflection", 300)
        page.click("#reflection"); page.type("#reflection", "마음이 한결 가벼워졌습니다. 모두 평안하시기를.", delay=40)
        page.wait_for_timeout(600)
        page.click("#finish"); page.wait_for_timeout(1200)
        page.evaluate("() => window.scrollTo(0,0)")
        cap("수행 기록은 차곡차곡", "단계마다 남긴 일지와 시간이 저장됩니다")
        page.wait_for_timeout(3600)

        # 6. 소원 기원
        mark("wish")
        go("/wish/buseoksa")
        cap("소원 기원", "누구를 위한, 어떤 소원인지 소원지를 씁니다")
        page.click('[data-k=for_whom] .chip[data-v="child"]'); page.wait_for_timeout(500)
        page.click('[data-k=category] .chip[data-v="suneung"]'); page.wait_for_timeout(500)
        page.click("#wishText")
        page.type("#wishText", "우리 아이가 그동안 애쓴 만큼, 시험장에서 떨지 않고 실력을 다 보여 주기를.", delay=40)
        page.wait_for_timeout(500)
        scroll_to("#toBow", 500)
        page.click('[data-k=target] .chip[data-v="3"]'); page.wait_for_timeout(700)
        page.click("#toBow"); page.wait_for_timeout(1000)
        page.evaluate("() => window.scrollTo(0,0)")
        cap("정성을 다해 큰절을", "합장 → 무릎 꿇기 → 이마를 바닥에 → 접족례 → 일어서기")
        page.wait_for_timeout(1000)
        page.click("#bowBtn")                       # 첫 배는 '정성껏' 속도로 끝까지
        page.wait_for_function("() => document.querySelector('#bowCount').textContent.startsWith('1')", timeout=30000)
        cap("108배까지, 염주 알이 하나씩 밝아집니다", "속도를 고르고 '이어서 절하기'로 계속 올릴 수 있어요")
        page.click('#speed .chip[data-s="2.4"]')
        page.click("#autoBow")
        page.click("#bowBtn")
        page.wait_for_selector("#offerBtn:not([hidden])", timeout=60000)
        page.wait_for_timeout(1200)
        page.click("#offerBtn"); page.wait_for_timeout(1600)

        # 7. 편지
        mark("letter")
        page.evaluate("() => window.scrollTo(0,0)")
        cap("소원이 편지가 되어", "한지 편지지에 담긴 소원과 절의 수")
        page.wait_for_timeout(3600)
        scroll_to(".share", 300)
        cap("링크로 마음을 전하세요", "받는 사람은 로그인 없이 편지를 열어 봅니다 (이메일은 보이지 않아요)")
        page.click("#copyBtn"); page.wait_for_timeout(3200)
        share = page.input_value("#shareUrl")
        go(share.split("#", 1)[1])
        page.wait_for_timeout(2600)

        # 8. 나의 기록
        mark("my")
        go("/my")
        cap("나의 기록", "템플스테이와 소원 편지를 언제든 다시 펼쳐 봅니다")
        page.wait_for_timeout(3800)

        # 9. 범종
        mark("bell")
        go("/")
        cap("산사의 범종 소리와 함께", "은은한 범종이 배경에 은은하게 울립니다 (기본 켜짐)")
        page.hover("#musicBtn"); page.wait_for_timeout(3600)

        # 10. 모바일 — 휴대폰 크기 브라우저 화면을 캡처해 휴대폰 틀 안에 보여 준다
        mark("mobile")
        import base64
        mctx = browser.new_context(viewport={"width": 376, "height": 784}, device_scale_factor=2,
                                   is_mobile=True, has_touch=True, locale="ko-KR",
                                   storage_state=ctx.storage_state())
        m = mctx.new_page()
        page.evaluate("""() => {
          const w = document.createElement('div'); w.id = 'vphone';
          w.style.cssText = 'position:fixed;inset:0;z-index:9998;display:grid;place-items:center;opacity:0;transition:opacity .8s;background:radial-gradient(ellipse at 50% 40%,#fbf4e4,#e6d6b6)';
          w.innerHTML = '<div style="width:404px;height:812px;border-radius:52px;background:#1d1a17;padding:14px;box-shadow:0 30px 60px rgba(0,0,0,.35);margin-bottom:60px">'
            + '<img id="vshot" style="width:376px;height:784px;border-radius:40px;display:block;background:#f3ead8"></div>';
          document.body.appendChild(w);
          requestAnimationFrame(() => w.style.opacity = '1');
        }""")
        cap("휴대폰에서도 편하게", "모바일 화면에 맞춰 그대로 즐길 수 있어요")

        def show():
            data = base64.b64encode(m.screenshot(type="jpeg", quality=88)).decode()
            page.evaluate("(d) => { document.getElementById('vshot').src = 'data:image/jpeg;base64,' + d }", data)

        def mscroll(total, steps=10):
            for _ in range(steps):
                m.evaluate("(d) => window.scrollBy(0, d)", total // steps)
                m.wait_for_timeout(40); show()

        m.goto(BASE + "/#/"); m.wait_for_load_state("networkidle"); m.evaluate("document.fonts.ready"); m.wait_for_timeout(500)
        show(); page.wait_for_timeout(2200)
        mscroll(700); page.wait_for_timeout(1200)
        m.evaluate("() => { location.hash = '/temples' }"); m.wait_for_timeout(900); m.evaluate("() => window.scrollTo(0,0)")
        show(); page.wait_for_timeout(1400)
        mscroll(900); page.wait_for_timeout(1000)
        m.evaluate("() => { location.hash = '/temple/buseoksa' }"); m.wait_for_selector(".dharma"); m.wait_for_timeout(1500); m.evaluate("() => window.scrollTo(0,0)")
        show(); page.wait_for_timeout(1400)
        mscroll(m.evaluate("() => document.querySelector('.dharma').getBoundingClientRect().top - 50"), 14)
        page.wait_for_timeout(2400)
        m.evaluate("() => { location.hash = '/my' }"); m.wait_for_timeout(1300); m.evaluate("() => window.scrollTo(0,0)")
        show(); page.wait_for_timeout(2600)
        mctx.close()
        page.evaluate("() => document.getElementById('vphone').remove()")

        # 11. 엔딩
        mark("outro")
        nocap()
        card("마음의 평화를", "지금 산사의 마음에 들어와 보세요", "sansa-api-vn7n.onrender.com")
        page.wait_for_timeout(5200)
        mark("end")

        video = page.video.path()
        ctx.close(); browser.close()
        (OUT / "marks.json").write_text(json.dumps({"video": str(video), "marks": marks}, ensure_ascii=False, indent=1), encoding="utf-8")
        print("VIDEO", video)


if __name__ == "__main__":
    run()
