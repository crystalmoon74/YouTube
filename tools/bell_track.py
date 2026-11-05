# 영상용 배경음: 사이트의 범종(templeBell)과 같은 방식으로 합성한 범종 + 아주 옅은 바람 소리
import sys
import wave

import numpy as np

SR = 44100
dur = float(sys.argv[1])
hits = [float(x) for x in sys.argv[2].split(",")]
out = sys.argv[3]

n = int(SR * dur)
mix = np.zeros(n)
rng = np.random.default_rng(7)


def bell(t0, vol=1.0, base=82.0):
    start = int(t0 * SR)
    # 당목 타격음: 낮게 걸러진 짧은 잡음
    k = int(0.25 * SR)
    noise = rng.uniform(-1, 1, k) * (1 - np.arange(k) / k) ** 3
    noise = np.convolve(noise, np.ones(40) / 40, mode="same")
    seg = noise * 0.9
    end = min(n, start + k)
    mix[start:end] += seg[: end - start] * vol * 0.6
    # 배음: [비, 음량, 지속, 맥놀이 폭]
    for ratio, amp, d, beat in [(1, 1.0, 14, 0.35), (1.68, 0.7, 11, 0.5), (2.5, 0.45, 9, 0.7),
                                (3.4, 0.3, 7, 0.9), (4.5, 0.18, 5, 1.2), (6.1, 0.1, 3.5, 1.6)]:
        length = min(n - start, int(d * SR))
        if length <= 0:
            continue
        t = np.arange(length) / SR
        env = np.minimum(t / 0.03, 1.0) * np.exp(-t * (6.9 / d))
        for det in (-beat / 2, beat / 2):
            mix[start:start + length] += np.sin(2 * np.pi * (base * ratio + det) * t) * env * amp * 0.11 * vol


for i, h in enumerate(hits):
    bell(h, 1.0 if i == 0 else 0.8)

# 아주 옅은 산바람(분홍 잡음에 가까운 저역 잡음)
wind = np.cumsum(rng.uniform(-1, 1, n))
c = np.cumsum(np.concatenate([[0.0], wind]))
half = SR // 2
idx = np.arange(n)
lo, hi = np.clip(idx - half, 0, n), np.clip(idx + half, 0, n)
wind -= (c[hi] - c[lo]) / np.maximum(hi - lo, 1)   # 1초 이동평균을 빼서 느린 흔들림만 남김
wind /= np.max(np.abs(wind)) + 1e-9
mix += wind * 0.012

# 앞뒤 페이드, 정규화
fade = int(1.5 * SR)
mix[:fade] *= np.linspace(0, 1, fade)
mix[-fade * 2:] *= np.linspace(1, 0, fade * 2)
mix = mix / np.max(np.abs(mix)) * 0.8
pcm = (mix * 32767).astype(np.int16)
stereo = np.column_stack([pcm, pcm]).ravel()
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(stereo.tobytes())
print("ok", out, dur)
