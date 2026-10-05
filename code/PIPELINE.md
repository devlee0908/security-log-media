# security.log 게시 파이프라인 (예약 작업용 지침)

## 파일
- template.html : 슬라이드 템플릿/애니메이션
- render.py     : `python render.py post.json out/<YYYY-MM-DD>` → 01..NN.mp4/jpg + manifest.json + caption.txt
- publish.py    : `python publish.py publish out/<날짜>` (Cloudinary 업로드 → IG 캐러셀 게시)
                  `python publish.py series TIPS` (다음 시리즈 번호) / `python publish.py recent` (최근 캡션, 중복 주제 확인)
- posts/EXAMPLE.json : 게시물 스펙 정답 예시 (구조를 그대로 따를 것)

## 카테고리 (cover.cat)
| cat | 다루는 것 | 표지 우측 표기 |
|---|---|---|
| NEWS | 실제 발생한 해킹·유출 사고 | 날짜(자동) |
| CVE | 지금 패치해야 할 취약점 (제품/버전/CVSS/조치) | 날짜(자동) |
| WEEKLY | 한 주 핵심 5개 요약 (일요일) | 날짜(자동) |
| TREND | 공격 수법 흐름·리포트 통계 | `"no"`: series 번호 |
| TIPS | 일반인용 생활 보안 실천법 | `"no"`: series 번호 |
| WORDS | 보안 용어 쉬운 설명 | `"no"`: series 번호 |

## 슬라이드 구성 (7장 권장)
1. cover (영상) 2~5. content n=1..4 (영상) 6. summary (이미지) 7. follow (이미지)

## 표지 애니메이션 (cover.anim) — 주제에 맞게 선택, 같은 장면 연속 사용 지양
- rain   : 계정/비밀번호 탈취 {word, wordSize}
- gauge  : 취약점 점수 {score, label}
- ransom : 랜섬웨어 {files:[8개 파일명], banner}
- otp    : MFA/인증 팁 {app, code(6자리)}
- week   : 주간 정리 {title:"WEEK 41", items:[[["라벨","r|y|g"],...] x7요일]}
- call   : 보이스피싱/전화 사기 {caller, number, initial, warn}

## 본문 애니메이션 (content.anim)
- terminal  : {title, count, countLabel, rows:[["계정명", 성공여부bool] x≤9]}
- timeline  : {marks:[0..n-1], pos:[분 단위 0~7], total, label}
- network   : {center, centerSub, nodes:[5개], flag}
- checklist : {items:[4개 짧은 문장]}

## 문구 규칙
- 제목 2줄(\n), 강조는 <b>…</b>. 본문 강조는 [대괄호] → 초록 강조.
- 본문 3~4문장, 사실은 반드시 출처 기사로 확인. 추측·과장 금지.
- summary.source 에 출처(기관/매체, 날짜) 명시.
- caption: 따옴표 훅 한 줄 → 짧은 단락 3~4개 → "👉🏻 보안 소식 놓치지 않으려면? @security.log" → "💾 저장해두고 팀에 공유하세요 :)" → 해시태그 8~10개 → 마지막 줄 `security.log · <CAT>` (시리즈형은 `security.log · TIPS #003`).
