// 다시 운전 — 영상 시연용 자동 운전 (화살표·Q/E/D/P 키 입력만 흉내 냄)
// 직선 구간: 2차로 중앙선을 순수 추종. 우회전: 교차로 안까지 들어간 뒤 핸들을 끝까지 꺾어 회전.
// car.x, car.y 는 뒷바퀴 축 중심.
window.__auto = (opts) => {
  const DS = window.DS, run = DS._run, inp = DS.input;
  const o = Object.assign({ cruise: 7.5, slow: 3.2, turnV: 2.0, look: 12, enter: 6.6, fast: 1 }, opts || {});
  const st = { phase: 'start', t0: performance.now(), log: [], leg: 0 };
  const key = (k, v) => inp.setDown(k, v);
  const tap = (k) => inp.press(k);
  const say = (m) => { st.log.push(Math.round((performance.now() - st.t0) / 100) / 10 + 's ' + m); };
  const SP = run.world.SP, LANE = 5.25;
  const dirOf = (i) => { const th = DS.cardTh(run.legCard(i)); return { th, f: { x: Math.sin(th), y: -Math.cos(th) }, r: { x: Math.cos(th), y: Math.sin(th) } }; };
  const N = (i) => ({ x: run.nodes[i].c * SP, y: run.nodes[i].r * SP });
  const nLeg = run.nodes.length - 1;

  // 다음 교차로 중심 기준, 진행 방향으로의 위치(음수 = 아직 도착 전)
  const along = (i) => { const { f } = dirOf(i), n = N(i + 1), c = run.car; return (c.x - n.x) * f.x + (c.y - n.y) * f.y; };
  const lateral = (i) => { const { r } = dirOf(i), n = N(i), c = run.car; return (c.x - n.x) * r.x + (c.y - n.y) * r.y; };

  // 원하는 바퀴 각도(rad, +가 오른쪽)로 핸들을 맞춘다
  function steerTo(sd) {
    const cur = run.car.steer;
    key('right', cur < sd - 0.025);
    key('left', cur > sd + 0.025);
  }
  // maxAhead: 이보다 먼 보행자는 무시 (우회전 직전에는 교차로 건너편 횡단보도를 보지 않음)
  function pedAhead(maxAhead, maxLat) {
    const car = run.car, f = { x: Math.sin(car.th), y: -Math.cos(car.th) };
    for (const p of run.world.peds) {
      if (p.done) continue;
      const dx = p.x - car.x, dy = p.y - car.y;
      const ah = dx * f.x + dy * f.y, lat = Math.abs(dx * f.y - dy * f.x);
      if (ah > 2 && ah < (maxAhead || 22) && lat < (maxLat || 9)) return true;
    }
    return false;
  }
  // 게임 규칙과 같은 기준: 횡단보도에 들어가기 직전, 그 횡단보도에 걷는(도로 위) 보행자가 가까이 있거나 대기 중인 보행자가 바로 옆이면 정지
  function cwBlock() {
    const car = run.car, w = run.world, c = car.center, f = car.fwd;
    const front = { x: c.x + f.x * (car.spec.length / 2 + 1.2), y: c.y + f.y * (car.spec.length / 2 + 1.2) };
    for (const cw of w.crosswalks) {
      const q = cw.rect;
      const insideC = c.x > q.x0 - 0.5 && c.x < q.x1 + 0.5 && c.y > q.y0 - 0.5 && c.y < q.y1 + 0.5;
      if (insideC) continue;
      const dx = Math.max(q.x0 - front.x, 0, front.x - q.x1), dy = Math.max(q.y0 - front.y, 0, front.y - q.y1);
      const dd = Math.hypot(dx, dy);
      if (dd > 3.5 || dd < 0.25) continue;            // 이미 앞부분이 들어갔으면 멈추지 않고 빠져나간다
      const near = (p, r) => Math.hypot(p.x - c.x, p.y - c.y) < r;
      if (w.peds.some((p) => p.cw === cw && ((p.phase === 'walk' && w.pedOnRoad(p) && near(p, 13)) || (p.phase === 'wait' && near(p, 10))))) return true;
    }
    return false;
  }
  // 신호등: 정지선(횡단보도 앞) 1m 전에 멈추도록 거리에 맞춰 감속. 반환값 = 허용 속도(Infinity 면 제한 없음)
  const STOP_A = -(run.world.HW + 5 + 1) - 3.9;     // 뒷바퀴 축 기준 정지 위치 (교차로 중심에서)
  function redLimit(i) {
    if (i >= nLeg - 1) return Infinity;
    const a = along(i);
    if (a < -60 || a > STOP_A + 1.5) return Infinity;   // 이미 정지선을 넘었으면 그대로 진행
    const g = run.legSeg(i), node = run.nodes[i + 1];
    const s = run.world.lightState(node.c, node.r, g.axis);
    if (!s) return Infinity;
    const remain = STOP_A - a;
    if (s === 'G') {
      // 정지선 근처에서 서 있다가 출발할 때는 녹색이 5초 이상 남았을 때만
      const left = run.world.lightRemain(node.c, node.r, g.axis);
      if (Math.abs(run.car.v) < 0.5 && remain < 6 && left < 5) return remain <= 0.3 ? 0 : Math.sqrt(2 * 2.2 * remain);
      return Infinity;
    }
    if (s === 'R') st.yGo = -1;
    // 적색 우회전은 하지 않고 녹색을 기다린다 (시연에서 보행자와 겹치지 않도록)
    // 황색: 편하게 멈출 수 없으면(필요 감속 > 3.2) 그대로 통과 — 실제 운전 요령과 같음
    if (s === 'Y' && st.yGo !== i && run.car.v * run.car.v / (2 * Math.max(remain, 0.1)) > 3.2) st.yGo = i;
    if (st.yGo === i) return Infinity;
    return remain <= 0.3 ? 0 : Math.sqrt(2 * 2.2 * remain);
  }
  function goalAlong() {
    const g = run.legSeg(nLeg - 1);
    const { f } = dirOf(nLeg - 1), c = run.car;
    const sGoal = g.s0 + (g.s1 - g.s0) * run.course.goalT;
    const s = g.axis === 'v' ? c.y : c.x;
    return (s - sGoal) * (g.axis === 'v' ? -f.y : f.x) * -1 * -1;
  }

  const iv = setInterval(() => {
    if (!DS._run || run.dead) { clearInterval(iv); return; }
    const car = run.car, now = performance.now() - st.t0;
    if (run.st.paused || run.st.finished) return;
    const i = st.leg;
    if (i < nLeg - 1) { const g = run.legSeg(i), nd = run.nodes[i + 1]; st.dbg = { leg: i, phase: st.phase, a: +along(i).toFixed(1), light: run.world.lightState(nd.c, nd.r, g.axis), v: +car.v.toFixed(1) }; }
    if (st.phase === 'start') {
      key('down', true);
      if (now > 700 && !st.dTap) { tap('d'); st.dTap = 1; say('D'); }
      if (now > 1600 && !st.qTap) { tap('q'); st.qTap = 1; say('signal L'); }
      if (now > 2800) { key('down', false); st.phase = 'drive'; say('go'); }
      return;
    }
    if (st.phase === 'stop') { ['up', 'left', 'right'].forEach((k) => key(k, false)); key('down', true); return; }

    if (st.phase === 'turn') {
      window.__speed = 1;
      const { th } = dirOf(i + 1);
      const d = DS.angleDiff(th, car.th);
      key('right', d > 0.04); key('left', d < -0.04);
      if (pedAhead(9, 3.5) || cwBlock()) { key('up', false); key('down', true); }
      else { key('up', car.v < o.turnV); key('down', car.v > o.turnV + 0.8); }
      if (Math.abs(d) < 0.1) { st.leg = i + 1; st.phase = 'drive'; say('turn done -> leg ' + st.leg); }
      return;
    }

    // ---- 직선 주행 ----
    if (i < nLeg - 1 && run.expectedTurn(i) === 0 && along(i) > 0) { st.leg = i + 1; say('straight -> leg ' + st.leg); return; }
    const { f, r, th } = dirOf(i);
    const lat = lateral(i), err = lat - LANE;
    const want = th + Math.atan2(-err, o.look);
    const d = DS.angleDiff(want, car.th);
    steerTo(Math.max(-0.45, Math.min(0.45, 1.4 * d)));
    // 합류가 끝나면 왼쪽 깜빡이 끄기
    if (i === 0 && car.signal === -1 && Math.abs(err) < 0.4 && now > 5000) { tap('q'); say('signal off'); }
    // 회전 후 바깥 차로로 붙을 때: 오른쪽 깜빡이 켜고, 다 붙으면 끄기
    if (i > 0 && st.merge !== i && err < -1.0 && car.signal !== 1) { tap('e'); st.merge = i; say('merge signal R'); }
    if (i > 0 && st.merge === i && Math.abs(err) < 0.35 && car.signal === 1) { tap('e'); st.merge = -1; say('merge done'); }

    let target = o.cruise;
    const turnNext = i < nLeg - 1 && run.expectedTurn(i) === 1;
    if (turnNext) {
      const a = along(i);
      if (a > -40 && car.signal !== 1) { tap('e'); say('signal R'); }
      if (a > -25) target = o.slow;
      if (a > -o.enter - 3) target = o.turnV;
      if (a >= -o.enter) { st.phase = 'turn'; say('turn start'); return; }
    }
    if (i === nLeg - 1) {
      const g = run.legSeg(i), s = g.axis === 'v' ? car.y : car.x;
      const sGoal = g.s0 + (g.s1 - g.s0) * run.course.goalT;
      const remain = (sGoal - s) * g.dir;
      if (remain < 12) target = o.slow;
      if (remain < 1.5) {
        key('up', false); key('down', true);
        if (Math.abs(car.v) < 0.05 && car.gear !== 'P') { tap('p'); say('P at goal'); st.phase = 'stop'; }
        return;
      }
    }
    const pedLimit = turnNext ? Math.max(3, -along(i) - 4) : 22;
    const ped = pedAhead(pedLimit) || cwBlock(), lim = redLimit(i), red = lim === 0;
    target = Math.min(target, lim);
    const stop = ped || red;
    if (stop) { key('up', false); key('down', true); }
    else { key('down', car.v > target + 1.0); key('up', car.v < target); }
    if (st.wasStop !== stop) { say(stop ? 'stop' : 'resume'); st.wasStop = stop; if (!stop) st.resumed = (st.resumed || 0) + 1; }
    const nearTurn = i < nLeg - 1 && run.expectedTurn(i) === 1 && along(i) > -26;
    const nearGoal = i === nLeg - 1;
    const waitingRed = red && Math.abs(car.v) < 0.1;
    window.__speed = (o.fast > 1 && st.resumed >= 1 && !nearGoal && (waitingRed || (!nearTurn && !ped))) ? o.fast : 1;
  }, 25);
  st.kill = () => { clearInterval(iv); ['up', 'down', 'left', 'right'].forEach((k) => key(k, false)); };
  window.__autoState = st;
  return 'ok';
};
