# START HERE — 아요코딩 하네스 사용 설명서

이 저장소는 **앱을 기획 → 제작 → 출시 → 운영 → 개선**하는 전 과정을 Claude Code 위에서 돌리기 위한 작업 틀(하네스)입니다.
코딩을 몰라도 순서대로 따라 하면 됩니다. 용어가 낯설면 `docs/GLOSSARY.md`.

---

## 0. 처음 한 번: 설치 확인 (PC 마다)

PowerShell(`PS C:\...>` 화면)에서 한 줄씩 입력해 **네 가지 모두 버전 숫자가 나와야** 합니다. 훅(안전장치)이 전부 Python 으로 돌아가므로 Python 이 없으면 안전장치가 **조용히 꺼진 채** 작업됩니다.

| 확인 | 명령 | 없으면 |
|------|------|--------|
| Git | `git --version` | `winget install --id Git.Git -e` |
| Python 3.10+ | `python --version` | `winget install Python.Python.3.12 --override "/quiet PrependPath=1"` |
| Node 20+ (테스트·문법검사용) | `node --version` | `winget install OpenJS.NodeJS.LTS` |
| Claude Code | `claude --version` | `irm https://claude.ai/install.ps1 \| iex` 후 `claude` 로 로그인 |
| 화면 캡처 (선택, 디자인 확인용) | 앱 폴더에서 `python scripts/screenshot.py design-system/styleguide.html` → `캡처:` 줄이 나오면 됨 | `python -m pip install playwright` 다음 `python -m playwright install chromium` (약 150MB 내려받음. 병원 방화벽에서 막히면 집 PC 에서만 써도 됨) |

설치 후에는 PowerShell(VS Code 포함)을 **완전히 닫고 다시** 엽니다. 그리고 한 번만:
```powershell
git config --global user.name "Ayo"
git config --global user.email "GitHub 가입 이메일"
git config --global init.defaultBranch main
```
GitHub 에 처음 push 할 때 브라우저 로그인 창이 뜨면 **Sign in with your browser** 로 승인합니다.

---

## 0-1. 30초 요약
| 하고 싶은 것 | Claude Code 에 입력 |
|---|---|
| 새 앱 시작 | PowerShell 에서 `scripts\new-project.ps1 앱이름` → 안내된 폴더에서 `claude` → `/start 앱 한 줄 설명` |
| 이미 만든 앱을 이 틀로 | PowerShell 에서 `scripts\adopt.ps1 앱폴더경로` → 그 폴더에서 `claude` → `/adopt` |
| 틀을 고친 뒤 기존 앱들에 반영 | `scripts\update-harness.ps1 앱폴더경로` (도구만 갱신, 문서·코드는 보존 · 앱에 맞게 고친 명령·스킬은 그 앱의 `.claude\harness-keep.txt` 에 적어 두면 지킴) |
| 배포했는데 망가짐 | `/rollback 무엇이 잘못됐는지` |
| 기능 하나 추가 | `/feature 기능 설명` |
| 화면 시안 2~3개 보고 고르기 | `/design 화면 설명` |
| 화면 더 예쁘게 | `ui-designer 로 {화면} 개선안 줘` |
| 버그 고치기 | `/fix 어느 화면에서 뭘 했더니 뭐가 잘못됐다` |
| 배포 | `/ship` |
| 지금 상태 | `/status` |
| 다른 PC 와 맞추기 | `/sync` |
| 그만할 때·대화가 길어졌을 때 | `/handoff` → `/clear` |
| 뭐가 바뀌었는지 | `/explain` |

---

## 1. 이 틀이 하는 일

| 비유 | 여기서는 |
|------|---------|
| 회사 규칙집 | `CLAUDE.md` + `docs/` (AI 가 매번 읽는다) |
| 업무 지시서 | `/feature` `/fix` 같은 명령어, 큰 작업은 `phases/` 의 step 파일 |
| 전문 담당자들 | `.claude/agents/` — 설계·테스트·디버그·검토·개인정보·화면 점검·화면 디자인·문서 담당 8명 + 부를 때만 쓰는 점검 3명(접근성·속도·서버 보안) |
| 사내 노하우 문서 | `.claude/skills/` — 디자인·측정 데이터 표시·사진·리포트·Supabase·배포·개인정보·git·계획 |
| 디자인 견본 | `design-system/` — 디자인 값(tokens.css)과 컴포넌트 견본(styleguide.html). 새 화면은 여기서 복사 |
| 자동 안전장치 | `.claude/hooks/` — 위험 명령 차단, 비밀키 차단, 문법 검사, 커밋 전 검사, 다른 PC 변경 알림 |
| 큰 공사용 자동 실행기 | `scripts/execute.py` — step 을 하나씩 새 AI 세션에 시키고 결과를 기록 |

**두 가지 작업 트랙**
- **작은 작업(매일)**: `/feature`, `/fix` — 대화하면서 한 기능·한 버그. 설계 → 테스트 → 구현 → 검토 → 문서 → 커밋까지 한 번에.
- **큰 작업(가끔)**: `/harness` → `python scripts/execute.py` — 새 앱 전체, 큰 구조 변경. 단계별로 자동 실행.

---

## 2. 폴더와 파일

| 경로 | 무엇 | 사람이 고치나 |
|------|------|------------|
| `CLAUDE.md` | 공통 규칙(고정) + 프로젝트 규칙(빈칸) | 빈칸만, `/start` 가 채움 |
| `docs/PRD.md` | 무엇을 누구를 위해 왜 만드나 | `/start` |
| `docs/ARCHITECTURE.md` | 어떻게 짜여 있나(폴더·데이터 흐름·보안) | `/start`, 바뀌면 `docs-keeper` |
| `docs/ADR.md` | 왜 그렇게 정했나 (공통 ADR-000 시리즈는 기본값) | 결정이 바뀔 때 |
| `docs/DATA.md` | 다루는 모든 데이터와 민감도·보관·삭제 | 새 필드 전에 |
| `docs/UI_GUIDE.md` | 디자인 표준(무채색·버튼 단어 표준) | 거의 안 고침 |
| `docs/TESTING.md` | 자동 테스트 규칙 + 폰 수동 점검표 | 점검 항목 추가 |
| `docs/RELEASE.md` | 버전 규칙, 배포 절차, 스토어 정보 보관함 | 스토어 정보 |
| `docs/PRIVACY.md` | 동의 문구, 개인정보처리방침 재료 | 책임자·이메일 |
| `docs/BACKLOG.md` | 할 일·아이디어 | `/backlog` |
| `docs/CHANGELOG.md` | 변경 이력(사용자 말로) | `/ship` 이 씀 |
| `docs/GLOSSARY.md` | 용어집 | — |
| `docs/HANDOFF.md` | 인수인계서 — 하던 일·다음 할 일 (최신 하나만) | `/handoff` 가 씀 |
| `docs/TASTE.md` | 디자인 취향 기록 (좋다·싫다 한 것이 쌓임) | 말하면 AI 가 기록 |
| `design-system/tokens.css` | 디자인 값(색·글자·여백)과 기본 컴포넌트 CSS | 거의 안 고침 |
| `design-system/styleguide.html` | 컴포넌트 견본 페이지 (브라우저로 열어 보기) | 새 모양이 필요할 때 추가 |
| `scripts/screenshot.py` | 폰 크기 화면 캡처 → `.shots/` (git 에 안 올라감) | 그대로 |
| `scripts/app_capture.py` | **로그인 뒤 화면** 캡처 (테스트 계정, agent-browser) | 그대로 |
| `scripts/browser_check.py` | 시나리오(JSON) 대로 앱을 실제 브라우저에서 움직여 **기능이 끝까지 되는지** 확인 (가짜 자료 넣기·버튼·파일 내려받기) | 그대로 |
| `.claude/harness-keep.txt` (앱에만, 선택) | `update-harness` 가 덮어쓰지 말아야 할 앱 전용 명령·스킬 목록 | 앱에 맞게 고칠 때 |
| `.claude/capture.json` | 로그인 캡처할 배포 주소 (비밀값 없음) | 앱마다 한 번 |
| `docs/PLANS/` | 승인받은 계획서 보관함 (`/plan`, 위험한 `/feature`·`/fix` 가 만듦) | 승인할 때 |
| `.claude/commands/` | 슬래시 명령 21개 | 그대로 |
| `.claude/agents/` | 전문 담당 11명 (8명 + 부를 때만 3명) | 그대로 |
| `.claude/skills/` | 노하우 41개 (기본 23 + 외부 18: Superpowers·UI UX Pro Max·Caveman) | 디자인 기본값 바꿀 때만 |
| `.claude/hooks/` + `settings.json` | 자동 안전장치 | 그대로 |
| `THIRD_PARTY_NOTICES.md` | 가져온 외부 스킬의 출처·라이선스(MIT) | 그대로 |
| `scripts/new-project.ps1` | 새 프로젝트 폴더 만들기 | 그대로 |
| `scripts/adopt.ps1` | 기존 앱에 하네스 넣기 | 그대로 |
| `scripts/update-harness.ps1` | 기존 앱의 하네스 도구를 최신 틀로 갱신 | 그대로 |
| `scripts/execute.py` | 큰 작업 자동 실행기 (`--skip-preflight` 로 사전 점검 생략 가능) | 그대로 |
| `.env.example` | 서버용 비밀키 이름 예시(값 없음). anon 키는 `js/config.js` 에 | 복사해 `.env` 로 |
| `.mcp.json.example` | Claude Code 가 Supabase 를 직접 보게 하는 설정 예시 | 쓸 때 복사 |

> `docs/` 중 PRD·ARCHITECTURE·ADR·DATA·UI_GUIDE·TESTING 은 큰 작업의 **매 step 마다 AI 에게 통째로 전달**됩니다. 나머지(BACKLOG·CHANGELOG·GLOSSARY·RELEASE·PRIVACY)는 필요할 때만 읽습니다.

---

## 3. 도구 한눈에 보기

### 명령어 (대화창에 입력)
| 명령 | 언제 | 하는 일 |
|------|------|--------|
| `/start 설명` | 새 프로젝트 처음 | 질문 3개 이내로 기획 문서 채움 |
| `/adopt` | 기존 앱 가져온 직후 | 코드를 읽어 문서를 역으로 작성, 표준과 다른 점 진단 |
| `/plan 설명` | 구현 전에 계획만 | 계획서(`docs/PLANS/`) 작성 → 승인 대기. 코드는 안 건드림 |
| `/feature 설명` | 기능 추가 | 설계→(위험하면 계획 승인)→테스트→구현→검토→문서→커밋 |
| `/fix 증상` | 버그 | 재현→원인→(위험하면 계획 승인)→수정→재발 방지 |
| `/ship` | 배포 | 점검→버전 4곳→CHANGELOG→폰 점검표→push |
| `/status` | 언제든 | 현황표 + 지금 할 일 1개 |
| `/sync` | PC 바꿀 때 | pull·충돌 해결·push 대행 |
| `/handoff` | 그만할 때, 대화가 길어졌을 때 | 인수인계서(`docs/HANDOFF.md`) 한 장 작성·올리기 → 다음 대화·다른 PC 가 자동으로 이어감 |
| `/explain` | 궁금할 때 | 최근 변경을 쉬운 말로 |
| `/wait-what` | 방금 AI 설명이 이해 안 될 때 | 같은 내용을 더 쉬운 말·비유로 다시 |
| `/grill-with-docs 계획` | 큰 기능 전, 생각 정리 | 질문 라운드로 빈틈 찾기 + 앱 용어·결정을 용어집·ADR 에 기록 |
| `/improve-codebase-architecture` | 파일이 너무 커졌을 때, 몇 주에 한 번 | 구조 정리 후보를 그림 보고서로 → 고른 것을 질문으로 다듬어 `/plan` 으로 |
| `/retro` | 작업이 끝난 뒤 | AI 가 헤맨 곳을 찾아 하네스 고칠 점을 심각한 순서로 제안 |
| `/design 화면` | 화면 모양을 정할 때 | 시안 2~3개를 만들어 나란히 비교 → 고른 이유를 TASTE.md 에 기록. 앱 코드는 안 건드림 |
| `/review` | 수동 검토 | 규칙 준수 점검표 |
| `/privacy` | 개인정보 기능 뒤 | 노출 점검 |
| `/privacy-policy` | 출시 전 | 개인정보처리방침 페이지 생성 |
| `/backlog 항목` | 아이디어 떠오를 때 | BACKLOG 정리 |
| `/harness` | 큰 작업 | step 설계·실행 준비 |
| `/rollback 문제` | 배포 후 사고 | 마지막 배포 되돌리고 새 버전으로 재배포 |

### 에이전트 (명령어가 알아서 부름. "architect 로 설계해줘" 처럼 직접 불러도 됨)
`ui-checker`·`docs-keeper`·`tester` 는 규칙 대조가 주 일이라 **Sonnet** 으로 고정(토큰 절약). 나머지는 지금 고른 모델을 따른다.
| 이름 | 역할 | 코드 수정 |
|------|------|---------|
| `architect` | 설계안·단계 쪼개기·ADR 제안 | ✗ |
| `tester` | 자동 테스트 작성·실행, 수동 점검 항목 | 테스트 파일만 |
| `debugger` | 근본 원인 추적 | ✗ |
| `reviewer` | 버그·규칙 위반 검토 | ✗ |
| `privacy-guard` | 개인정보·비밀키·동의·RLS 점검 | ✗ |
| `ui-checker` | 디자인 규칙 위반 점검 (색·버튼 단어·4가지 상태·견본·리포트·취향) | ✗ |
| `ui-designer` | 화면을 폰 크기로 찍어 보고 "더 좋아질 곳" 개선안 | ✗ |
| `docs-keeper` | 코드 ↔ 문서 동기화 | 문서만 |
| `a11y-checker` | 접근성(글자 대비·크기·터치 영역·화면 읽기 이름표) 점검 — "접근성 점검" 이라고 부를 때만 | ✗ |
| `speed-checker` | 폰 속도(LCP·INP·CLS) 점검과 개선 순서 — "속도 점검" 이라고 부를 때만 | ✗ |
| `supabase-checker` | 서버 표·보안 규칙(RLS)·함수·버킷 점검 — "서버 점검" 이라고 부를 때만 | ✗ |

### 스킬 (AI 가 필요할 때 스스로 읽음)
| 이름 | 내용 |
|------|------|
| `clean-ui` | 심플·깔끔 CSS 기본값, 금지 패턴 |
| `mobile-webapp` | 폰 웹앱 기본 구성(HTML/JS + GitHub Pages + 필요 시 Supabase) |
| `camera-photo` | 촬영·축소·회전·IndexedDB·캔버스 점찍기·공유 |
| `report-print` | A4 여러 장 리포트·PDF 저장 |
| `supabase-safe` | 테이블·RLS·비공개 버킷·키 구분·기기→서버 이전 |
| `pwa-release` | manifest·서비스워커 버전·GitHub Pages·Google Play(TWA) |
| `korean-privacy` | 동의·서명·보관·처리방침·Play 데이터 안전 |
| `git-two-pc` | 두 PC 작업, 충돌, 되돌리기 |
| `plan-gate` | 계획 승인이 필수인 작업 판정 기준과 계획서 양식 |
| `ui-polish` | 심플하지만 고급스럽게 — 시선 순서·정렬·여백 리듬·글자·마감 점검 10가지 |
| `doc-grilling` | 질문 라운드로 다듬기 + 용어집·ADR 기록 방법 |
| `codebase-design` | 코드 구조 정리의 말과 원칙 (깊은 모듈·이음매·삭제 시험) |
| `app-capture` | 로그인 뒤 화면 캡처 방법과 개인정보 규칙 (테스트 계정만) |
| `measure-viz` | 측정 데이터 표시 — 숫자 표기·정상 범위 막대·좌우 비교·추이 그래프·사진 위 측정점 |
| `browser-check` | 기능이 실제 브라우저에서 끝까지 되는지 시나리오 한 장으로 확인 (`scripts/browser_check.py`) |
| `data-migration` | 저장 형식을 바꿀 때 기존 회원 자료를 지키는 규칙 — 바꾸면 안 되는 이름·예전 자료 '모름' 처리·빈 값·예전 자료로 시험 |
| `export-privacy` | (자동) 엑셀·PDF·이미지 등 앱 밖으로 나가는 파일의 개인정보 체크리스트 — 이름 대신 코드·그림 속 글자·동의한 회원만 사진·철회 처리 |
| `ux-writing` | (자동) 화면 문구 규칙 — 말투 하나로·오류는 '무엇이 안 됐는지 + 할 일'·표준 단어·전문용어 빼기 |

**외부 문서 도구**: Context7 — 외부 라이브러리·서비스의 최신 사용법을 찾아 준다. 저장소에 설치하는 것이 아니라 claude.ai 계정의 커넥터(연결 도구)로 쓴다. 연결이 안 돼 있으면 claude.ai → 설정 → 커넥터에서 Context7 을 켠다. CLAUDE.md 개발 프로세스에 '사용법은 Context7 로 확인' 규칙이 있다.

**외부 스킬** (출처 `THIRD_PARTY_NOTICES.md`)
| 언제 | 스킬 |
|------|------|
| 큰 기능일 때만 자동 | `brainstorming`(만들기 전에 질문으로 원하는 것 분명히 → `docs/PLANS/` 계획서 → 승인 뒤 `/feature`) |
| 상황이 맞으면 자동 | `systematic-debugging`(원인부터 찾기) · `test-driven-development`(테스트 먼저) · `verification-before-completion`(완료라고 말하기 전 확인) · `receiving-code-review`(리뷰 받아 반영) · `dispatching-parallel-agents`(독립 작업 동시에) · `writing-skills`(스킬 만들기) |
| `/이름` 으로 부를 때만 | `writing-plans` · `executing-plans` · `subagent-driven-development` · `using-git-worktrees` · `finishing-a-development-branch` · `requesting-code-review` · `ui-ux-pro-max`(디자인 자료집 — 결과는 UI_GUIDE·TASTE 에 맞춰 고름) · `caveman`·`ultracave`·`megacave`·`caveman-help`(짧은 말투로 토큰 절약) |

### 훅 (항상 켜져 있음)
| 때 | 하는 일 |
|----|--------|
| Claude Code 켤 때 | 다른 PC 에서 올린 변경이 있으면 `git pull` 하라고 알림 |
| 명령 실행 전 | 폴더 통째 삭제·강제 push·작업 버리기 등 되돌릴 수 없는 명령 차단 |
| 커밋 직전 | `.env`·키 파일·5MB 이상 파일, 커밋 내용 속 비밀키, `.claude/pii-names.local.txt` 에 적은 실제 회원 이름이 있으면 차단 (이름 목록 파일은 PC 에만 두고 git 에 안 올라감) |
| 파일 쓰기 전 | API 키·service_role 키가 코드에 들어가면 차단 |
| 파일 쓴 직후 | js 문법·json 형식·html 태그 짝 + html 안 `<script>` 문법 검사 → 틀리면 즉시 고치게 |
| 작업 마칠 때 | `package.json` 있으면 lint → build → test |

---

## 4. 처음 한 번: 새 앱 시작

1. **폴더 만들기** — 이 틀 폴더에서 PowerShell:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\new-project.ps1 my-app
   ```
   끝나면 스크립트가 알려 주는 `cd "…"` 와 `claude` 두 줄을 그대로 입력합니다. (문서 폴더가 OneDrive 에 있어도 맞는 경로를 알려 줍니다.)
2. **기획** — `/start 트레이너가 회원 체형 사진을 찍어 리포트를 만드는 앱` 처럼 한 줄. 질문에 답하면 PRD·ARCHITECTURE·DATA·CLAUDE.md 가 채워진다. 끝나면 `/explain` 으로 무엇이 정해졌는지 확인.
3. **커밋** — `git add -A` → `git commit -m "docs: 기획 문서"`.
4. **GitHub 저장소 만들기** — github.com 에서 New repository(이름 = 폴더명, Public, README 없이) → 안내된 두 줄:
   ```powershell
   git remote add origin https://github.com/ayoajeyo/my-app.git
   git push -u origin main
   ```
   Settings → Pages → Branch `main` 으로 배포 주소를 켠다.
5. **만들기** — 작은 앱이면 `/feature` 를 기능마다 반복. 큰 앱이면 `/harness` → 승인 → `python scripts/execute.py 0-mvp`.
6. **출시** — `/privacy-policy` → `/ship` → 폰에서 확인 → (스토어는 `pwa-release` 스킬·RELEASE.md).

## 5. 매일: 기능·버그·배포
```
claude            ← 켜면 훅이 "pull 하세요" 를 알려줄 수 있음 → /sync
/status           ← 오늘 할 일 확인 (승인 대기 계획도 보임)
/plan …           ← 선택. 구현 없이 계획서만 먼저 보고 싶을 때
/feature …        ← 또는 /fix …  (위험한 작업은 계획서를 보여 주고 "승인" 을 기다림)
/ship             ← 폰 점검표 확인 후 배포
```

### 디자인 (보기 좋게)
화면 디자인은 이 순서로 돌아갑니다. 쓸수록 내 취향이 쌓여 다음 화면이 더 잘 맞습니다.
| 단계 | 무엇 | 도구 |
|------|------|------|
| 기준 | 색·글꼴(Pretendard)·여백·버튼 모양 | `docs/UI_GUIDE.md`, `design-system/` |
| 고르기 | 모양이 고민되면 시안 2~3개 비교 | `/design 화면 설명` |
| 만들기 | 규칙대로 + 고급스럽게 다듬기 | `clean-ui`·`ui-polish`·`measure-viz` 스킬 (자동) |
| 확인 | 폰 크기 사진을 찍어 규칙 점검 + 개선안 | `scripts/screenshot.py` → `ui-checker` → `ui-designer` (`/feature` 가 자동) |
| 기억 | "이건 좋다·싫다" 라고 말하면 기록 | `docs/TASTE.md` |
- 견본 보기: 앱 폴더에서 `python -m http.server 8000` → 브라우저로 http://localhost:8000/design-system/styleguide.html
- 직접 사진 찍기: `python scripts/screenshot.py index.html --full` → `.shots/` 폴더에 PNG
- 화면 캡처 도구(Playwright)가 없는 PC 에서는 사진 없이 코드만 보고 점검합니다. 설치는 0장 표 마지막 줄.
- **로그인 뒤 화면**(회원 목록·리포트)까지 AI 가 보게 하려면 PC 마다 한 번:
  ```powershell
  npm i -g agent-browser
  agent-browser install
  python scripts/app_capture.py login     # 창이 뜨면 '테스트 계정'으로 로그인 → Enter
  ```
  실제 회원이 있는 계정으로 로그인하지 마세요. 확인: `python scripts/app_capture.py status` · 지우기: `… forget`

### 구조도 (선택: Archify)
코드나 업무 흐름을 눌러 보는 그림(HTML)으로 보고 싶을 때. PC 에 한 번만 설치합니다(Node 필요, 하네스 안에는 넣지 않음):
```powershell
npx skills add tt-a1i/archify -g
```
쓰기: Claude Code 에서 `Archify로 측정 → 저장 → 리포트 흐름을 그려줘`. 그림은 `.archify/` 에 저장되고 GitHub 에는 올라가지 않습니다(.gitignore). 업데이트 확인 통신은 하네스 설정에서 꺼 두었습니다.

### 코드 지도 (선택: Graphify)
파일이 많은 앱에서 "이 기능은 어디와 연결돼?" 를 지도(지식 그래프)로 보고 싶을 때. PC 에 한 번만 설치합니다(Python 필요, 하네스 안에는 넣지 않음 — `graphify install` 이 PC 마다 최신 스킬을 깔아 줌):
```powershell
python -m pip install --user graphifyy
python -m graphify install
```
패키지 이름은 `graphifyy`(y 두 개)가 맞습니다. 쓰기: Claude Code 에서 `/graphify .`(처음 한 번 지도 만들기) → `/graphify query "알림은 어디서 보내?"`. 결과는 `graphify-out/` 에 저장되고 GitHub 에는 올라가지 않습니다(.gitignore). 처음 만들 때 토큰이 많이 들어, **부를 때만** 씁니다.

### 토큰 아끼기 (사용량 한도 덜 쓰기)
AI 는 대화가 길수록 앞 내용을 매번 다시 읽어서 같은 질문도 점점 비싸집니다.
| 언제 | 할 일 | 효과 |
|------|------|------|
| 평소 | `/model opusplan` 한 번 (계속 유지됨) | Plan 모드(`Shift+Tab`)에서만 Opus 로 설계, 코드 작성은 Sonnet |
| 큰 기능 시작 | `Shift+Tab` 으로 Plan 모드 → 계획 → 승인 → 실행 | 비싼 두뇌는 설계에만 |
| 한 기능이 끝날 때 | `/handoff` → `/clear` | 긴 대화 대신 인수인계서 한 장으로 다음 작업 |
| 대화가 길어졌는데 같은 일을 계속 | `/compact` | 대화를 요약해 줄임 (중요한 결정은 `/handoff` 가 더 안전) |
| PC 를 바꿀 때 | `/handoff` (자동으로 올림) → 다른 PC 에서 `git pull` → `claude` | 켜자마자 "이어서 할 일" 이 뜸 |
- 검토·점검 같은 일은 명령어가 **서브에이전트**(별도 AI)에게 맡기고 요약만 받아서 메인 대화가 가볍게 유지됩니다. 직접 할 일은 없습니다.

### 계획 먼저 (승인이 필요한 때)
개인정보·서버(Supabase)·삭제·결제·로그인·배포 설정·큰 변경이 걸리면 `/feature` `/fix` 가 **구현 전에 계획서를 만들고 멈춥니다.** 요약을 읽고 `승인` 이라고 답하면 그때 구현합니다. 고칠 곳이 있으면 번호로 알려 주세요.
- 직접 계획부터 받고 싶으면 `/plan 하려는 일`.
- 승인된 계획으로 구현: `/feature 계획: docs/PLANS/파일이름.md`
- Claude Code 기본 기능도 있습니다: `Shift+Tab` 으로 Plan 모드(읽기만 하는 모드)로 바꾸면 승인 전까지 아무것도 고치지 않습니다.

## 6. 기존 앱 가져오기 (예: posture-check)
```powershell
cd $HOME\Documents\harness_framework
powershell -ExecutionPolicy Bypass -File scripts\adopt.ps1 $HOME\Documents\posture-check
```
스크립트가 알려 주는 `cd` 와 `claude` 를 입력한 뒤 `/adopt 바디샷 체형 측정 앱`.
`/adopt` 가 코드를 읽어 문서를 채우고, 표준과 다른 점(🔴 비밀키·버전 불일치 등)을 BACKLOG 에 넣는다. 그다음부터 `/feature` `/fix` `/ship` 을 그대로 쓴다.

## 7. 큰 작업 실행기 (`/harness` + execute.py)
1. `/harness` → 논의 → "구현 계획 짜 줘" → 승인 → `phases/` 생성
2. `git add -A && git commit -m "docs: 구현 계획"` (실행기는 저장 안 된 변경이 있으면 멈춤)
3. `python scripts/execute.py 0-mvp` (`--push` 붙이면 끝나고 push)
4. 결과: `phases/0-mvp/index.json` 의 `status`. `error`/`blocked` 는 원인 해결 → `"pending"` 으로 바꾸고 재실행
5. 끝나면 `git checkout main` → `git merge feat-0-mvp` → `/ship`

실행기 사전 점검(빈칸·미커밋·claude 설치)을 건너뛰려면 `--skip-preflight`. 한 step 이 30분을 넘기면 자동 중단되어 `error` 로 기록된다.

## 7-1. 틀 자체를 고쳤을 때
틀(`harness_framework`)의 훅·명령·스킬을 고쳤다면 → 틀 폴더에서 커밋·push → 각 앱 폴더에 `scripts\update-harness.ps1 앱경로` 로 반영. 문서와 코드는 건드리지 않고 도구만 바뀐다. 앱에 맞게 고친 명령·스킬이 있으면 먼저 그 앱의 `.claude\harness-keep.txt` 에 한 줄씩 적어 둔다(예: `.claude\commands\ship.md`) — 적지 않은 것은 틀 것으로 바뀐다.

---

## 8. 자주 하는 실수
| # | 실수 | 결과 | 이렇게 |
|---|------|------|-------|
| 1 | `{ }` 빈칸을 두고 실행 | 실행기가 멈춤 / AI 가 엉뚱하게 만듦 | `/start` 로 채우기 |
| 2 | 원본 틀 폴더(`harness_framework`)에서 앱 작업 | 틀이 앱 하나로 오염 | 항상 `new-project.ps1` 로 복사 |
| 3 | `/ship` 없이 push | 버전 안 올라 폰에 옛 화면 | 배포는 `/ship` 만 |
| 4 | PC 바꾸고 pull 안 함 | 충돌 | 켤 때 알림 → `/sync` |
| 5 | 비밀키를 코드에 | 훅이 막음. 이미 올라갔으면 키 교체 | `.env` |
| 6 | 실제 회원 데이터로 테스트 | 유출 위험 | 홍길동·010-0000-0000 |
| 7 | 한 step 에 일 몰아넣기 | 3회 재시도 후 error | 한 step = 한 모듈 |
| 8 | 지시서에 "아까 말한 대로" | 새 세션은 모름 | 전부 적기 |
| 9 | `python3` 입력 | Windows 는 못 찾음 | `python` |
| 10 | 실행기가 **승인 없이** 돌아간다는 걸 모름 | 파일 수정·명령 실행을 묻지 않음 | git 관리 폴더에서만, 훅이 위험 명령은 막음 |
| 11 | 요청 안 한 기능이 끼어듦 | 범위가 커지고 버그 | CLAUDE.md 규칙: BACKLOG 에만 적음 |
| 12 | 사진·zip 을 커밋 | 훅이 5MB 이상 차단 | 코드 저장소엔 코드만 |
| 13 | 동의 전에 촬영 | 법적 문제 | `korean-privacy` 스킬 규칙 |
| 14 | `claude` 미설치·미로그인 | 실행기 첫 단계 실패 | `claude --version` 확인 |

---

## 9. 더 알아보기
- Claude Code 문서: https://code.claude.com/docs
- 이 틀의 원본: jha0313/harness_framework (구조 아이디어) → ayoajeyo/harness_framework (사업용으로 확장)
