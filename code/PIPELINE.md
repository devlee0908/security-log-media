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

## 주간 편성 (한국 시간)
- 아침 작업(매일 05:53): 월~토 NEWS 1건, 일요일 WEEKLY 1건(일요일 NEWS 없음).
- 저녁 작업(17:53): 화 CVE / 수 TIPS / 금 TREND / 토 WORDS. 아침 NEWS 와 주제 중복 금지.

## 슬라이드 구성 (카테고리별, 최대 10장 = 인스타 API 한도)
cover(영상) → content n=1.. (영상) → summary(이미지) → follow(이미지). 짧게 끝내지 말고 충분히 풀어 쓸 것.
- NEWS 9~10장: 표지 → 무슨 일 → 경위·기간 → 규모·유출 항목 → 수법·원인 → 왜 중요 → 당국·기업 대응 → 2차 피해·주의 → 내가 할 일 → 요약 → 팔로우
- CVE 7~9장: 표지(점수) → 제품·버전 → 취약점 내용 → 악용 여부(KEV) → 영향 범위 → 패치·완화 → 확인 방법 → 요약 → 팔로우
- TIPS 7~9장: 표지 → 이런 상황 → 왜 위험 → 따라하기 3~4단계 → 확인 → 요약 → 팔로우
- TREND 8~10장: 표지 → 핵심 수치 → 흐름 3~4장 → 의미 → 대응 → 요약 → 팔로우
- WORDS 6~8장: 표지 → 한 줄 정의 → 비유 → 실제 사례 → 공격 방식 → 방어 → 요약 → 팔로우
- WEEKLY 8장: 표지(week) → TOP5 각 1장 → 다음 주 일정 → 요약 → 팔로우 (10장 이내)

## 장면 다양성 규칙
- 최근 2주 게시물에서 쓴 표지 장면은 다시 쓰지 말 것. 본문도 한 게시물 안에서 같은 장면은 최대 2번.
- 그날 주제에 맞는 장면이 없으면 template.html 의 ANIM 에 새 장면 함수를 설계해 추가(기존 헬퍼 bgPro·panel·nodeBadge·flowLine·orb·withShadow 사용, 6초 루프, 캔버스 높이 h 안에서만 그리기, 선·점·패킷은 노드보다 먼저 그려 글자 위로 지나가지 않게).

## AI 이미지 규칙 (Gemini, ~/.secrets/gemini_key 와 gen_image.py 가 있을 때만)
- 범위: WORDS·TIPS 우선(표지 1 + 본문 1), NEWS 는 표지만 하루 1장, TREND 는 표지만 선택, CVE·WEEKLY 사용 금지.
- 이미지는 배경으로만 사용. 한글·숫자·로고·제목은 항상 코드로 얹는다.
- 금지: 실제 기업·기관 로고, 실존 인물 얼굴, 읽을 수 있는 글자, 공포 조장·선정적 이미지.
- 생성: `python gen_image.py "<영어 장면 묘사>" assets/<날짜>-<cat>-<번호>.png --ratio 4:5` (본문용은 --ratio 4:3). 실패 시 종료코드 1 → 코드 장면 사용.
- 사용: 해당 슬라이드를 `"anim":"photo", "data":{"src":"assets/<파일>.png", "label":"(본문만, 선택) 짧은 라벨"}` 로 지정. 표지 제목·태그는 기존처럼 HTML 로 얹힘.
- 장면 묘사는 비유·분위기 중심(예: 피싱=어두운 바다 위 빛나는 낚싯바늘). 게시물 내용을 사실처럼 보이게 하는 장면(실제 건물·사건 현장 재현) 금지.
- 생성 후 Read 로 직접 확인. 문제 있으면 최대 2회 재생성, 그래도 안 되면 코드 장면으로 대체.

## 수동 이미지 요청 (gen_image.py 가 실패할 때, 당분간 기본 방식)
- 게시 흐름을 멈추지 말 것: 먼저 코드 장면으로 렌더해서 승인 요청을 보낸다.
- AI 이미지가 효과적인 슬라이드(AI 이미지 규칙의 범위 안, 게시물당 최대 2장)가 있으면, 승인 요청 메시지 끝에 아래 형식으로 덧붙인다.
  "🎨 선택: 아래 프롬프트로 Gemini 앱에서 이미지를 만들어 첨부해 주시면 N장을 교체해 다시 보여드릴게요."
  각 이미지마다: [슬라이드 번호·용도] + Gemini에 그대로 붙여넣을 한국어 프롬프트 한 덩어리.
- 프롬프트 작성 규칙: 세로 4:5 비율(본문용은 가로 4:3), 장면·구도·색감·조명을 구체적으로, 하단 40%는 글자를 얹을 어두운 여백,
  "글자·숫자·로고·브랜드·국기·실존 인물 얼굴 없음"을 반드시 포함. 브랜드 톤: 어두운 배경 + 카테고리 색 네온 포인트.
- 사용자가 이미지를 첨부하면 assets/ 로 복사 → 해당 슬라이드를 anim "photo" 로 바꿔 그 슬라이드만 다시 렌더 → 다시 승인 요청.
- 사용자가 이미지 없이 '게시'라고 하면 코드 장면 그대로 게시.

## 표지 배경
- 카테고리별 배경 분위기·제목 강조색은 cover.cat 으로 자동 적용(NEWS 그린, CVE 레드, TREND 오렌지, TIPS 옐로, WEEKLY 블루, WORDS 퍼플). 따로 지정하지 말 것.
- 그림 속 선·점이 글자 위로 지나가지 않는지 렌더 후 프레임으로 확인.

## 표지 애니메이션 (cover.anim)
- 규칙: 표지는 그날 사건을 상징하는 장면이어야 함. 최근 게시물(`publish.py recent` 캡션/주제)과 같은 장면 반복 금지.
- 맞는 장면이 없으면 template.html 의 ANIM 에 새 장면 함수를 추가해서 사용(기존 함수 스타일: grid 배경, 레드/그린 포인트, 6초 루프).
- rain   : 계정/비밀번호 탈취 {word, wordSize}
- gauge  : 취약점 점수 {score, label}
- ransom : 랜섬웨어 {files:[8개 파일명], banner}
- otp    : MFA/인증 팁 {app, code(6자리)}
- week   : 주간 정리 {title:"WEEK 41", items:[[["라벨","r|y|g"],...] x7요일]}
- call   : 보이스피싱/전화 사기 {caller, number, initial, warn}
- dual   : 보안 도구의 악용·양면성 {left, right, chip, flash}
- breach : 여러 기관 연쇄 침해 {bot:"AI BOT?", label:"BREACHED", nodes:[["기관명","피해규모"] x≤6]}
- registry : 협력사·정식 권한 악용으로 대량 유출 {region, total(숫자), label, nodes:["원천","경유","유출처"], ok, bad}

## 본문 애니메이션 (content.anim)
- terminal  : {title, count, countLabel, rows:[["계정명", 성공여부bool] x≤9]}
- timeline  : {marks:[0..n-1], pos:[분 단위 0~7], total, label}
- network   : {center, centerSub, nodes:[4~6개], flag}  ※ 노드 수는 제목·본문의 숫자(예: '6곳')와 반드시 일치
- checklist : {items:[4개 짧은 문장]}
- console   : {title, lines:[["작업","상태","r|g"] x≤6]}  (로그/콘솔 화면)
- loop      : {steps:[4~6개], center, sub}  (반복 순환 구조)
- span      : 탐지까지 걸린 기간 {days, label, events:[["날짜","설명"] x3]}
- idcard    : 유출된 개인정보 항목 {head, fields:[["항목","마스킹 값"] x3], note, total, unit}
- quote     : 공식 발언 + 대응 현황 {quote(\n 2줄), who, chips:[["텍스트","g|y"] x3]}
- scam      : 2차 피해 사칭 메시지 예시 {msgs:[["[발신]","짧은 문구"] x4], note}
- photo     : AI 배경 이미지 {src, label?}  (AI 이미지 규칙 참고)
- map       : {total, label, local, localLabel, kx, ky}  (전 세계 분포 + 한국 강조)

## 문구 규칙
- follow 슬라이드 sub 는 EXAMPLE.json 문구 그대로 사용("저장해두고 동료에게 공유해 주세요"). '가족' 표현 사용 금지.
- 제목 2줄(\n), 강조는 <b>…</b>. 본문 강조는 [대괄호] → 초록 강조.
- 본문은 화면에 4줄 이내(약 110자 이내, 2~3문장). 넘치면 줄일 것. 사실은 반드시 출처 기사로 확인. 추측·과장 금지.
- 그림 속 개수·숫자는 제목/본문의 숫자와 반드시 일치시킬 것.
- 표지 제목은 2줄, 한 줄 약 12자(공백 포함) 이내. 넘치면 3줄로 밀리므로 줄일 것.
- 렌더 전 확인: content 슬라이드의 .text 하단이 1300px 를 넘지 않아야 함.
- summary.source 에 출처(기관/매체, 날짜) 명시.
- caption: 따옴표 훅 한 줄 → 짧은 단락 3~4개 → "👉🏻 보안 소식 놓치지 않으려면? @security.log" → "💾 저장해두고 동료에게 공유하세요 :)" → 해시태그 8~10개 → 마지막 줄 `security.log · <CAT>` (시리즈형은 `security.log · TIPS #003`).
