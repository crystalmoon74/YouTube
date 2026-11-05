# 녹화 영상(webm) + QR 배지 + QR 엔딩 + 범종 배경음 → 유튜브용 MP4(1920x1080, 30fps, H.264/AAC)
# 사용 예)
#   python compose.py --video rec/page@xxx.webm --start 2.3 --main 187.7 \
#       --end ../2026-11-sansa/end_qr.png --badge ../2026-11-sansa/badge.png --end-sec 12 \
#       --out ../2026-11-sansa/video.mp4
# --start: 녹화 앞부분(빈 화면)을 자를 초, --main: 본편 길이(초, 엔딩 카드 직전까지)
# 배경음은 bell_track.py 로 자동 생성한다 (12초마다 범종, 엔딩 시작에 한 번 더).
import argparse
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

ap = argparse.ArgumentParser()
ap.add_argument("--video", required=True)
ap.add_argument("--start", type=float, default=0.0)
ap.add_argument("--main", type=float, required=True)
ap.add_argument("--end", help="엔딩 이미지 (없으면 엔딩 없이)")
ap.add_argument("--end-sec", type=float, default=12.0)
ap.add_argument("--badge", help="모서리 QR 배지 (없으면 생략)")
ap.add_argument("--audio", help="배경음 wav (없으면 범종 자동 생성)")
ap.add_argument("--out", required=True)
a = ap.parse_args()

FF = imageio_ffmpeg.get_ffmpeg_exe()
here = Path(__file__).parent
end_sec = a.end_sec if a.end else 0
total = a.main + end_sec

audio = a.audio
if not audio:
    audio = str(Path(a.out).with_suffix(".bell.wav"))
    hits = [0.8] + [t for t in range(12, int(a.main) - 6, 12)] + ([round(a.main + 0.3, 1)] if a.end else [])
    subprocess.run([sys.executable, str(here / "bell_track.py"), str(total), ",".join(map(str, hits)), audio], check=True)

inputs = ["-ss", str(a.start), "-t", str(a.main), "-i", a.video]
fc = [f"[0:v]scale=1920:1080:flags=lanczos,fps=30,format=yuv420p,setsar=1[m0]"]
last = "m0"
idx = 1
if a.badge:
    inputs += ["-loop", "1", "-framerate", "30", "-t", str(a.main), "-i", a.badge]
    fc.append(f"[{idx}:v]scale=-1:150,format=rgba,fade=t=in:st=5.5:d=0.8:alpha=1,fade=t=out:st={a.main - 1.2}:d=0.8:alpha=1[b]")
    fc.append(f"[{last}][b]overlay=30:H-h-36:shortest=1[m1]")
    last = "m1"; idx += 1
fc.append(f"[{last}]fade=t=in:st=0:d=0.8" + ("" if a.end else f",fade=t=out:st={a.main - 1.5}:d=1.5") + "[mv]")
if a.end:
    inputs += ["-loop", "1", "-framerate", "30", "-t", str(end_sec), "-i", a.end]
    fc.append(f"[{idx}:v]scale=1920:1080,fps=30,format=yuv420p,setsar=1,fade=t=in:st=0:d=0.8,fade=t=out:st={end_sec - 1.5}:d=1.5[e]")
    fc.append("[mv][e]concat=n=2:v=1:a=0[v]")
    idx += 1
else:
    fc.append("[mv]null[v]")
inputs += ["-i", audio]

cmd = [FF, "-v", "error", "-stats", "-y", *inputs, "-filter_complex", ";".join(fc),
       "-map", "[v]", "-map", f"{idx}:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", a.out]
subprocess.run(cmd, check=True)
print("ok", a.out, f"{total:.1f}s")
