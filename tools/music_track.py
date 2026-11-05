# 영상용 잔잔한 배경 음악 합성 (밝은 코드 진행 + 부드러운 아르페지오). 저작권 걱정 없는 직접 합성 음원.
# 사용: python music_track.py <길이초> <출력.wav> [bpm]
import sys
import wave

import numpy as np

SR = 44100
dur = float(sys.argv[1]); out = sys.argv[2]; bpm = float(sys.argv[3]) if len(sys.argv) > 3 else 92
n = int(SR * dur); mix = np.zeros(n)
beat = 60 / bpm
# C - G - Am - F (각 2마디)
chords = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]
hz = lambda m: 440 * 2 ** ((m - 69) / 12)


def tone(t0, length, f, amp, attack=0.02, kind="sine"):
    a = int(t0 * SR); L = int(length * SR)
    if a >= n: return
    L = min(L, n - a); t = np.arange(L) / SR
    env = np.minimum(t / attack, 1) * np.exp(-t * 3.0 / length)
    w = np.sin(2 * np.pi * f * t) + (0.25 * np.sin(4 * np.pi * f * t) if kind == "pluck" else 0)
    mix[a:a + L] += w * env * amp


bar = 4 * beat; t = 0.0; k = 0
while t < dur:
    ch = chords[(k // 2) % 4]
    for m in ch[:3]:                       # 패드
        tone(t, bar * 1.05, hz(m - 12), 0.05, attack=0.4)
    tone(t, bar, hz(ch[0] - 24), 0.07, attack=0.05)   # 베이스
    for j in range(8):                     # 8분음 아르페지오
        m = ch[[0, 1, 2, 3, 2, 1, 2, 3][j]]
        tone(t + j * beat / 2, beat * 0.9, hz(m), 0.035, attack=0.005, kind="pluck")
    t += bar; k += 1

fade = int(2 * SR)
mix[:fade] *= np.linspace(0, 1, fade); mix[-fade:] *= np.linspace(1, 0, fade)
mix = mix / np.max(np.abs(mix)) * 0.55
pcm = (mix * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(np.column_stack([pcm, pcm]).ravel().tobytes())
print("ok", out, dur)
