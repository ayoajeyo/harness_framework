# 인수인계 (HANDOFF)

> `/handoff` 가 쓰는 문서. 대화를 새로 시작하거나 다른 PC 로 옮길 때 **이 문서 한 장**으로 이어간다 (긴 대화를 다시 읽지 않아 토큰을 아낌).
> 항상 **최신 상태 하나만** 둔다. 지난 기록은 CHANGELOG·docs/PLANS·git log 에 있다. 회원 실명·연락처는 쓰지 않는다.
> (틀 저장소의 인수인계다. `new-project.ps1` 은 새 앱에 이 내용 대신 빈 양식을 넣는다.)

상태: 진행 중
갱신: 2026-10-28

## 지금 하던 일
(없음 — 틀 작업은 모두 커밋·push 됨)

## 다음 할 일 (순서대로, 바로 입력할 명령 포함)
1. 바디샷·MEDICALLINK 작업이 끝나면 새 틀 반영 — 사용자가 "하네스 반영해줘". 먼저 각 앱 `.claude/harness-keep.txt` 에 화면 스킬(`clean-ui`·`measure-viz`·`ui-polish`·`camera-photo`)을 넣고(앱 색이 틀의 무채색과 다름), 앱이 커밋된 상태에서 `powershell -ExecutionPolicy Bypass -File scripts\update-harness.ps1 C:\Users\USER\BODYSHOT` / `…\Documents\MEDICALLINK`
2. MEDICALLINK 의 문서 커밋 `e4a8a20`(ADR-025·027 정책 식 바로잡음)은 그 앱의 다음 `/ship` 때 함께 올라감 — 따로 할 일 없음
3. 다른 PC 에서도 push 를 맡기려면 그 PC 터미널에서: `[IO.File]::WriteAllText("C:\Users\USER\Documents\harness_framework\.claude\settings.local.json", '{"permissions":{"allow":["Bash(git push)"]}}')` 후 Claude Code 다시 시작

## 이번에 끝낸 것 (2026-10-28)
- 이름: 회사 아요코딩(AYOCODING), 앱 바디샷 BODYSHOT, 표기 `made by AYOCODING` (소문자 `ayoajeyo` 는 GitHub 계정이라 그대로)
- 디자인 기본값 무채색: 흰 바탕 + 검정 `#1D1D1F` 주 버튼 + 회색, 기본 도형 선 아이콘 (ADR-000-11, TASTE 확정)
- 새 스킬 5개: `login-account`·`play-subscription`(바디샷), `multi-org`·`guest-link`·`web-push`(MEDICALLINK) — reviewer 지적 10건 반영 (ADR-000-10·12)
- `korean-privacy` 자동 삭제, UI_GUIDE PC 넓은 화면, `pwa-release` 배포 장소 고르기
- `new-project.ps1`: 새 앱에 `settings.local.json`·틀 계획서·틀 인수인계를 넘기지 않음

## 정해진 것 / 결정 대기
- 바디샷은 블루 그대로(앱만의 선택). 틀 기본은 무채색
- AI 도구 5개(gitingest 등)는 틀에 넣지 않음 → `Documents\AI도구` + BODYSHOT 볼트에 보관
- "볼트에 저장해줘" 규칙은 공통 규칙(`~/.claude/CLAUDE.md`)에 있음: MEDICALLINK 전용 → MEDICALLINK 볼트, 나머지 → BODYSHOT 볼트
- 결정 대기: 앱(홈 화면) 아이콘도 "흰 바탕 + 검정 기본 도형" 으로 할지 (UI_GUIDE 8번에 넣어 둠, 화면 안 아이콘만이면 그 줄 삭제)

## 주의할 점
- `.claude/settings.local.json`(이 PC 의 push 허용)은 `.gitignore` 됨. AI 가 직접 만들려 하면 자동 권한 검사가 막는다 — 사용자가 위 3번 명령으로
- `.claude/settings.json` 에 push 허용을 넣지 않는다 (모든 앱에 복사되어 `/ship` 점검을 건너뜀)
- 기존 앱 반영 전 지킬 목록 확인 필수 — 반영 스크립트는 스킬·명령·에이전트를 통째로 덮어씀
- 스킬 SQL 예시는 원본 마이그레이션 기준. MEDICALLINK ADR 문장의 `= any ((select …))` 식은 오류가 나니 따라 쓰지 않는다
- BODYSHOT 볼트에는 이번 작업 전부터 커밋 안 된 변경이 있어 볼트는 커밋하지 않았다

## 관련 파일
- `.claude/skills/{login-account,play-subscription,multi-org,guest-link,web-push}/SKILL.md`
- `docs/ADR.md`(000-10·11·12), `docs/TASTE.md`, `docs/UI_GUIDE.md`, `design-system/tokens.css`
- `docs/PLANS/2026-10-28-로그인-구독-스킬.md`, `docs/PLANS/2026-10-28-기관-손님링크-푸시-스킬.md`
- `scripts/new-project.ps1`, `scripts/update-harness.ps1`
