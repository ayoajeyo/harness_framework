---
description: 지금 프로젝트 진행 현황 — 작업 단계, 저장 안 된 변경, 다른 PC와의 동기화 상태
---

프로젝트 현황을 초보자가 한눈에 볼 수 있게 정리하라. 아무것도 수정하지 마라(읽기 전용).

확인할 것:
1. `phases/index.json`과 각 `phases/*/index.json` — 작업(phase)별 step 상태. 없으면 "아직 구현 계획 없음".
2. `git status` — 저장(커밋)하지 않은 변경 파일.
3. `git fetch` 후 `git status -sb` — GitHub보다 앞서 있는지(push 필요) 뒤처져 있는지(pull 필요).
4. `docs/`와 `CLAUDE.md`에 남은 `{ }` 빈칸 개수.

출력 형식:

| 항목 | 상태 | 할 일 |
|------|------|------|
| 구현 단계 | ✅ 3/5 완료 · ⏳ step3 대기 | `python scripts/execute.py 0-mvp` |
| 저장 안 된 변경 | 2개 파일 | 커밋 필요 |
| GitHub 동기화 | 뒤처짐 1개 | `git pull` |
| 기획 빈칸 | 0개 | — |

표 아래에 "지금 바로 할 일" 1가지만 제시하라.
