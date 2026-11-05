# Everyday AI Works — YouTube 동영상 제작

유튜브 채널 **Everyday AI Works** 에 올리는 "AI로 만든 작품 소개" 영상의 제작 도구·템플릿·작업 기록입니다.
사이트를 브라우저로 자동 조작하며 녹화하고, 자막·QR 코드·배경음을 붙여 유튜브용 MP4 를 만듭니다.

## 작업 원칙

- **사이트 테스트(리허설)는 1~2번만** 하고 바로 녹화합니다. 자동 조작이 완벽하지 않아도 더 다듬지 않습니다.
- 소개하는 사이트는 테스트로 만든 버전이므로, 영상에 **"※ 테스트로 만든 사이트라 아직 완전하지 않아요"** 를 항상 넣습니다
  (오프닝 노란 띠 · 5초 안내 카드 · 엔딩 · 설명란).
- 새 채널은 설명란 링크가 눌리지 않으므로 **영상 안 QR 코드**(모서리 배지 + 12초 QR 엔딩)로 접속을 안내합니다.

자세한 순서와 체크리스트: [YOUTUBE_UPLOAD_TEMPLATE.md](YOUTUBE_UPLOAD_TEMPLATE.md)

## 폴더 구조

```
YouTube/
├─ YOUTUBE_UPLOAD_TEMPLATE.md   새 영상 작업 템플릿 (영상마다 videos/<폴더>/작업내역.md 로 복사)
├─ tools/                       재사용 도구
│  ├─ record_demo.py            사이트 시연 녹화 예시 (산사의 마음)
│  ├─ qr_assets.py              QR 코드 · QR 엔딩 · 모서리 배지 (+ 판독 검사), --theme sansa|modern
│  ├─ compose.py                녹화본 + 배지 + 엔딩 + 배경음 → MP4 (1920x1080 / 30fps)
│  ├─ music_track.py            잔잔한 배경 음악 합성
│  ├─ bell_track.py             범종 배경음 합성
│  ├─ thumbnail.py              사진 + 제목 썸네일 (1280x720)
│  ├─ channel_art.py            채널 프로필·배너 만들기
│  └─ requirements.txt
├─ channel/                     채널 프로필(800x800) · 배너(2560x1440)
└─ videos/
   ├─ 2026-11-sansa-maeum/      산사의 마음 소개 (썸네일 · 설명란)
   └─ 2026-11-drive-sim/        다시 운전 소개 (녹화 스크립트 · 자동 운전 · 썸네일 · 설명란 · 작업내역)
```

> 영상(`*.mp4`)·녹화 원본(`rec/`)·음원(`*.wav`)은 용량이 커서 git 에 올리지 않고 로컬(`C:\AIAgent\YouTube`)에만 둡니다.

## 준비 (처음 한 번)

```bash
python -m venv C:/AIAgent/vid-env
```

```bash
C:/AIAgent/vid-env/Scripts/python -m pip install -r C:/AIAgent/YouTube/tools/requirements.txt
```

```bash
C:/AIAgent/vid-env/Scripts/python -m playwright install ffmpeg
```

브라우저는 PC 에 설치된 Microsoft Edge 를 사용합니다.

## 만든 영상

| 날짜 | 영상 | 길이 | 폴더 |
|---|---|---|---|
| 2026-11-04 | 산사의 마음 — 온라인 템플스테이 · 소원 기원 | 3:20 | `videos/2026-11-sansa-maeum/` |
| 2026-11-06 | 다시 운전 — 장롱면허 운전 시뮬레이션 | 3:36 | `videos/2026-11-drive-sim/` |
