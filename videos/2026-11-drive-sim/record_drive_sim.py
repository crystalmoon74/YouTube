# 「다시 운전」 소개 영상 녹화 — 공개 사이트(GitHub Pages)를 Edge 로 조작하며 1600x900 녹화
# 진도는 브라우저 localStorage 에만 저장되므로, 새 브라우저 프로필에서 처음 방문한 상태로 시연한다.
# 결과: rec/*.webm, rec/marks.json
import base64
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE / "rec"
OUT.mkdir(exist_ok=True)
BASE = "https://crystalmoon74.github.io/drive-sim/"
W, H = 1600, 900
NOTE = "※ 테스트로 만든 사이트라 아직 완전하지 않아요"
AUTOPILOT = (HERE / "drive_autopilot.js").read_text(encoding="utf-8")
marks = []
T0 = None

# 자막·타이틀 카드 (사이트 색에 맞춘 남색·파랑 계열)
OVERLAY = r"""
(() => {
  if (window.__cap) return;
  const font = document.createElement('link');
  font.rel = 'stylesheet';
  font.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;800;900&display=swap';
  document.head.appendChild(font);
  const css = document.createElement('style');
  css.textContent = `
  #vcap{position:fixed;left:50%;bottom:30px;transform:translate(-50%,20px);z-index:9999;opacity:0;min-width:46%;max-width:80%;
    padding:14px 34px 16px;text-align:center;pointer-events:none;background:rgba(15,23,42,.9);color:#fff;border-radius:18px;
    border:2px solid rgba(96,165,250,.6);box-shadow:0 10px 30px rgba(0,0,0,.35);transition:opacity .45s,transform .45s;font-family:'Noto Sans KR',sans-serif}
  #vcap.show{opacity:1;transform:translate(-50%,0)}
  #vcap b{display:block;font-weight:900;font-size:38px;line-height:1.2;color:#fde047}
  #vcap span{display:block;font-weight:500;font-size:22px;margin-top:6px;line-height:1.45}
  #vff{position:fixed;right:28px;top:84px;z-index:9999;display:none;padding:8px 18px;border-radius:999px;background:#ef4444;color:#fff;
    font:900 24px 'Noto Sans KR',sans-serif;box-shadow:0 6px 18px rgba(0,0,0,.3)}
  #vcard{position:fixed;inset:0;z-index:10000;display:grid;place-items:center;text-align:center;opacity:0;pointer-events:none;transition:opacity .9s;
    background:radial-gradient(ellipse at 50% 35%,#2563eb,#1e3a8a 60%,#0f172a);font-family:'Noto Sans KR',sans-serif;color:#fff}
  #vcard.show{opacity:1}
  #vcard .ico{font-size:110px;line-height:1}
  #vcard h1{font-weight:900;font-size:120px;margin:18px 0 0;letter-spacing:-2px}
  #vcard p{font-weight:500;font-size:34px;margin:18px 0 0;color:#dbeafe}
  #vcard .url{font-weight:800;font-size:34px;color:#fde047;margin-top:26px}
  #vcard .note{display:inline-block;font-weight:700;font-size:26px;color:#0f172a;background:#fde047;border-radius:999px;padding:8px 26px;margin-top:30px}
  #vcard.notice h1{font-size:64px;letter-spacing:0}
  #vcard.notice p{font-size:32px;line-height:1.6;white-space:pre-line}
  `;
  document.head.appendChild(css);
  const cap = document.createElement('div'); cap.id = 'vcap'; document.body.appendChild(cap);
  const ff = document.createElement('div'); ff.id = 'vff'; ff.textContent = '▶▶ 3배속'; document.body.appendChild(ff);
  const card = document.createElement('div'); card.id = 'vcard'; document.body.appendChild(card);
  setInterval(() => { ff.style.display = (window.__speed || 1) > 1 ? 'block' : 'none'; }, 150);
  window.__cap = (t, s) => {
    if (!t) { cap.classList.remove('show'); return; }
    cap.innerHTML = '<b></b><span></span>';
    cap.querySelector('b').textContent = t; cap.querySelector('span').textContent = s || '';
    cap.classList.add('show');
  };
  window.__card = (h, p, url, ico, note, kind) => {
    if (!h) { card.classList.remove('show'); return; }
    card.className = 'show ' + (kind || '');
    card.innerHTML = '<div><div class="ico"></div><h1></h1><p></p>' + (url ? '<div class="url"></div>' : '') + (note ? '<div class="note"></div>' : '') + '</div>';
    if (note) card.querySelector('.note').textContent = note;
    card.querySelector('.ico').textContent = ico || '🚗';
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
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(viewport={"width": W, "height": H}, record_video_dir=str(OUT),
                                  record_video_size={"width": W, "height": H}, locale="ko-KR")
        page = ctx.new_page()
        T0 = time.time()
        ov = lambda: page.evaluate(OVERLAY)

        def cap(t, s=""):
            ov(); page.evaluate("([t,s]) => window.__cap(t,s)", [t, s])

        def card(h, sub="", url="", ico="🚗", note="", kind=""):
            ov(); page.evaluate("([h,p,u,i,n,k]) => window.__card(h,p,u,i,n,k)", [h, sub, url, ico, note, kind])

        nocard = lambda: page.evaluate("() => window.__card && window.__card('')")
        nocap = lambda: page.evaluate("() => window.__cap && window.__cap('')")
        wait = page.wait_for_timeout

        def go(h):
            page.evaluate("(h) => { location.hash = h }", h); wait(700)

        def scroll_to(sel, offset=90):
            page.evaluate("([s,o]) => { const e=document.querySelector(s); window.scrollTo({top: e.getBoundingClientRect().top + scrollY - o, behavior:'smooth'}); }", [sel, offset])
            wait(1000)

        def top():
            page.evaluate("() => window.scrollTo({top:0, behavior:'smooth'})"); wait(700)

        page.goto(BASE + "#/home"); page.wait_for_load_state("networkidle")
        ov(); page.evaluate("document.fonts.ready"); wait(800)

        # 0. 오프닝
        mark("intro")
        card("다시 운전", "장롱면허 초보를 위한 운전 시뮬레이션", note=NOTE)
        wait(4200); nocard(); wait(900)
        mark("notice")
        card("먼저 알려 드려요", "이 영상의 사이트는 AI와 함께 테스트로 만든 버전이에요.\n화면·채점·법규 설명에 부족한 부분이 있을 수 있어요.\n실제 운전 전에는 꼭 운전 연수를 받고 공식 자료를 확인하세요.", ico="🛠️", kind="notice")
        wait(5200); nocard(); wait(900)

        # 1. 홈
        mark("home")
        cap("다시 운전대를 잡는 당신을 위해", "20년 만의 운전도 차근차근 — 설치 없이 웹에서 바로 연습해요")
        wait(3800)
        scroll_to(".grid-4", 120)
        cap("네 가지 연습 메뉴", "자동차 기능 · 운전 연습 · 주차 연습 · 법규 퀴즈")
        for k in range(1, 5):
            page.hover(f".grid-4 .menu-card:nth-child({k})"); wait(650)
        wait(1200)

        # 2. 자동차 기능
        mark("features")
        go("/features")
        cap("자동차 기능 알아보기", "운전석 그림의 번호를 누르면 설명과 사용 요령이 나와요")
        wait(1600)
        for sid in ["start", "signal", "gear"]:
            page.click(f'.hot[data-id="{sid}"]'); wait(1700)
        scroll_to(".gear-demo", 300)
        cap("기어 P · R · N · D", "눌러 보면 언제 쓰는지 바로 알려 줘요")
        for g in ["R", "N", "D"]:
            page.click(f'.gear-demo button[data-g="{g}"]'); wait(1100)
        top()
        page.click('.tab[data-tab="compare"]'); wait(400)
        cap("SUV vs 세단", "크기 감각과 시야 차이를 한눈에 비교")
        wait(2600)
        page.click('.tab[data-tab="warn"]'); wait(400)
        cap("계기판 경고등", "빨강 · 노랑 · 초록, 색깔로 급한 정도를 알 수 있어요")
        wait(2800)

        # 3. 운전 연습 — 선택
        mark("drive_select")
        go("/drive")
        cap("운전 연습", "차종과 코스(초급 · 중급 · 고급)를 고르고 탑승합니다")
        wait(1800)
        scroll_to('[data-course="easy"]', 200); wait(800)
        page.click("#goCheck"); wait(900)

        # 4. 탑승 점검 9단계
        mark("checklist")
        cap("출발 전 점검 9단계", "실제 차에 탈 때처럼 순서대로 확인하는 습관")
        wait(1200)
        for z in ["front", "right", "back", "left"]:
            page.click(f'.zone[data-z="{z}"]'); wait(500)
        wait(1000)
        cap("문 잠금 · 시트 · 거울", "슬라이더로 바른 자세와 거울 각도를 맞춰요")
        page.click("#dClose"); wait(500); page.click("#dLock"); wait(1000)
        for sid, v in [("#sPos", "81"), ("#sBack", "105"), ("#sHead", "60")]:
            page.fill(sid, v); wait(600)
        wait(500); page.click("#sNext"); wait(1000)
        for sid, v in [("#mRoom", "50"), ("#mSide", "25"), ("#mUp", "50")]:
            page.fill(sid, v); wait(600)
        wait(500); page.click("#mNext"); wait(1000)
        cap("안전벨트 · 시동 · 기어", "브레이크를 밟아야 시동과 기어 변경이 돼요")
        page.click("#bBtn"); wait(1300)
        page.click("#stBrake"); wait(600); page.click("#stBtn"); wait(1700)
        page.wait_for_selector('#clQ button[data-a="1"]'); wait(700)
        page.click('#clQ button[data-a="1"]'); wait(2000)
        # 시동 단계에서 밟은 브레이크가 그대로 유지되므로 바로 D → 주차 브레이크 해제
        page.click('.gear-demo button[data-g="D"]'); wait(600)
        page.click("#gEpb"); wait(2000)
        cap("출발 전 최종 확인", "깜빡이 → 거울 → 사각지대, 순서대로!")
        for k in ["sig", "mirror", "shoulder"]:
            page.click(f'[data-k="{k}"]'); wait(800)
        page.wait_for_selector("#ckGo"); wait(1200)
        page.click("#ckGo"); wait(1200)

        # 5. 주행
        mark("drive")
        cap("초급 코스 '동네 한 바퀴'", "내비게이션을 따라 목적지까지 — 100점에서 시작해 위반마다 감점")
        wait(2600)
        page.click("#mStart"); wait(200)
        page.evaluate("""() => { const r = DS._run, orig = r.step.bind(r);
          window.__speed = 1; r.step = (dt) => { for (let k = 0; k < (window.__speed || 1); k++) orig(dt); }; }""")
        page.evaluate(AUTOPILOT)
        page.evaluate("window.__auto({fast: 3})")
        cap("출발", "브레이크 밟고 D → 왼쪽 깜빡이 켜고 도로로 합류")
        wait(4500)
        cap("횡단보도 보행자 보호", "사람이 건너면 정지선 앞에서 멈춰요")
        page.wait_for_function("() => window.__autoState.log.some(l => l.includes('turn start'))", timeout=90000)
        cap("우회전", "오른쪽 깜빡이 켜고, 천천히 바깥 차로로")
        page.wait_for_function("() => window.__autoState.log.some(l => l.includes('turn done'))", timeout=60000)
        wait(1500)
        cap("신호등과 교차로", "신호 · 깜빡이 · 차로를 자동으로 채점해요")
        page.wait_for_function("() => DS._run && DS._run.st.finished", timeout=240000)
        page.evaluate("() => { window.__speed = 1 }")
        score = page.evaluate("() => DS._run.st.score")
        print("drive score", score, flush=True)
        cap("도착! 기어 P", "완전히 멈춘 뒤 P — " + ("위반 없이 100점" if score == 100 else f"{score}점, 놓친 부분은 결과 화면에서 알려 줘요"))
        wait(3200)
        page.wait_for_selector("#rRetry", timeout=15000); wait(400)
        cap("주행 결과", "합격 여부와 위반 항목, 잘한 점까지 정리해 줘요")
        wait(3800)

        # 6. 주차
        mark("parking")
        go("/parking")
        cap("주차 연습", "후면 · 전면 · 평행 · 좁은 지하주차장, 4가지 상황")
        wait(2600)
        page.click('[data-scene="rear"]'); wait(1000)
        page.click("#pDemo2"); wait(400)
        cap("시범 보기", "보라색 차가 이상적인 움직임을, 노란 고스트가 기준 위치를 보여 줘요")
        wait(6000)
        cap("예상 진행선 · 주차 센서", "후방카메라처럼 가이드라인을 보며 따라 해요")
        page.wait_for_function("() => document.getElementById('pDemoTag') && document.getElementById('pDemoTag').style.display === 'none'", timeout=40000)
        wait(800)

        # 7. 법규 퀴즈
        mark("quiz")
        go("/quiz")
        cap("법규 퀴즈 52문제", "바뀐 교통법규를 친절한 해설과 함께")
        wait(1800)
        page.click("#qQuick"); wait(1000)
        for n in range(2):
            ans = page.evaluate("""() => { const t = document.querySelector('.quiz-q').textContent.replace(/^Q\\.\\s*/, '');
              const q = DS.QUIZ.find((x) => x.q === t); return q ? q.a : 0; }""")
            wait(1800)
            page.click(f'.quiz-opt[data-i="{ans}"]'); wait(3300)
            if n == 0:
                cap("틀린 문제는 오답 노트로", "다시 풀며 확실하게 익혀요")
                page.click("#qNext"); wait(900)

        # 8. 휴대폰 화면
        mark("mobile")
        mctx = browser.new_context(viewport={"width": 376, "height": 784}, device_scale_factor=2, is_mobile=True,
                                   has_touch=True, locale="ko-KR", storage_state=ctx.storage_state())
        m = mctx.new_page()
        page.evaluate("""() => {
          const w = document.createElement('div'); w.id = 'vphone';
          w.style.cssText = 'position:fixed;inset:0;z-index:9998;display:grid;place-items:center;opacity:0;transition:opacity .8s;background:radial-gradient(ellipse at 50% 40%,#dbeafe,#93c5fd)';
          w.innerHTML = '<div style="width:404px;height:812px;border-radius:52px;background:#0f172a;padding:14px;box-shadow:0 30px 60px rgba(0,0,0,.35);margin-bottom:60px">'
            + '<img id="vshot" style="width:376px;height:784px;border-radius:40px;display:block;background:#fff"></div>';
          document.body.appendChild(w); requestAnimationFrame(() => w.style.opacity = '1'); }""")
        cap("휴대폰 · 태블릿에서도", "화면 아래 버튼으로 핸들 · 페달 · 기어를 조작해요")

        def show():
            d = base64.b64encode(m.screenshot(type="jpeg", quality=88)).decode()
            page.evaluate("(d) => { document.getElementById('vshot').src = 'data:image/jpeg;base64,' + d }", d)

        def mscroll(total, steps=10):
            for _ in range(steps):
                m.evaluate("(d) => window.scrollBy(0, d)", total // steps); m.wait_for_timeout(40); show()

        m.goto(BASE + "#/home"); m.wait_for_load_state("networkidle"); m.wait_for_timeout(500)
        show(); wait(2000); mscroll(700); wait(900)
        m.evaluate("() => { location.hash = '/features' }"); m.wait_for_timeout(900); m.evaluate("() => window.scrollTo(0,0)")
        show(); wait(1600)
        m.evaluate("() => { location.hash = '/drive' }"); m.wait_for_timeout(700)
        m.click("#goCheck"); m.wait_for_timeout(500)
        if m.query_selector("#ckSkip"):
            m.click("#ckSkip"); m.wait_for_timeout(900)
        m.evaluate("() => window.scrollTo(0,0)"); show(); wait(1200)
        m.click("#mStart"); m.wait_for_timeout(300)
        top_touch = m.evaluate("() => { const t = document.getElementById('touch'); return t ? t.getBoundingClientRect().top + scrollY - 420 : 0 }")
        m.evaluate("(y) => window.scrollTo(0, y)", top_touch); m.wait_for_timeout(300)
        for _ in range(8):
            show(); wait(250)
        wait(1200)
        mctx.close()
        page.evaluate("() => document.getElementById('vphone').remove()")

        # 9. 엔딩 (QR 엔딩은 compose 단계에서 붙인다)
        mark("outro")
        nocap()
        card("다시 운전", "오늘부터 천천히, 다시 운전대를 잡아 보세요", "crystalmoon74.github.io/drive-sim", note=NOTE)
        wait(4800)
        mark("end")

        video = page.video.path()
        ctx.close(); browser.close()
        (OUT / "marks.json").write_text(json.dumps({"video": str(video), "marks": marks}, ensure_ascii=False, indent=1), encoding="utf-8")
        print("VIDEO", video)


if __name__ == "__main__":
    run()
