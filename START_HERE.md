# START HERE — 아요바디요 하네스 사용 설명서

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
| 틀을 고친 뒤 기존 앱들에 반영 | `scripts\update-harness.ps1 앱폴더경로` (도구만 갱신, 문서·코드는 보존) |
| 배포했는데 망가짐 | `/rollback 무엇이 잘못됐는지` |
| 기능 하나 추가 | `/feature 기능 설명` |
| 버그 고치기 | `/fix 어느 화면에서 뭘 했더니 뭐가 잘못됐다` |
| 배포 | `/ship` |
| 지금 상태 | `/status` |
| 다른 PC 와 맞추기 | `/sync` |
| 뭐가 바뀌었는지 | `/explain` |

---

## 1. 이 틀이 하는 일

| 비유 | 여기서는 |
|------|---------|
| 회사 규칙집 | `CLAUDE.md` + `docs/` (AI 가 매번 읽는다) |
| 업무 지시서 | `/feature` `/fix` 같은 명령어, 큰 작업은 `phases/` 의 step 파일 |
| 전문 담당자들 | `.claude/agents/` — 설계·테스트·디버그·검토·개인정보·화면·문서 담당 7명 |
| 사내 노하우 문서 | `.claude/skills/` — 사진·리포트·Supabase·배포·개인정보·git |
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
| `docs/UI_GUIDE.md` | 디자인 표준(네이비 단일 포인트·버튼 단어 표준) | 거의 안 고침 |
| `docs/TESTING.md` | 자동 테스트 규칙 + 폰 수동 점검표 | 점검 항목 추가 |
| `docs/RELEASE.md` | 버전 규칙, 배포 절차, 스토어 정보 보관함 | 스토어 정보 |
| `docs/PRIVACY.md` | 동의 문구, 개인정보처리방침 재료 | 책임자·이메일 |
| `docs/BACKLOG.md` | 할 일·아이디어 | `/backlog` |
| `docs/CHANGELOG.md` | 변경 이력(사용자 말로) | `/ship` 이 씀 |
| `docs/GLOSSARY.md` | 용어집 | — |
| `.claude/commands/` | 슬래시 명령 14개 | 그대로 |
| `.claude/agents/` | 전문 담당 7명 | 그대로 |
| `.claude/skills/` | 노하우 8개 | 디자인 기본값 바꿀 때만 |
| `.claude/hooks/` + `settings.json` | 자동 안전장치 | 그대로 |
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
| `/feature 설명` | 기능 추가 | 설계→테스트→구현→검토→문서→커밋 |
| `/fix 증상` | 버그 | 재현 테스트→원인→수정→재발 방지 |
| `/ship` | 배포 | 점검→버전 4곳→CHANGELOG→폰 점검표→push |
| `/status` | 언제든 | 현황표 + 지금 할 일 1개 |
| `/sync` | PC 바꿀 때 | pull·충돌 해결·push 대행 |
| `/explain` | 궁금할 때 | 최근 변경을 쉬운 말로 |
| `/review` | 수동 검토 | 규칙 준수 점검표 |
| `/privacy` | 개인정보 기능 뒤 | 노출 점검 |
| `/privacy-policy` | 출시 전 | 개인정보처리방침 페이지 생성 |
| `/backlog 항목` | 아이디어 떠오를 때 | BACKLOG 정리 |
| `/harness` | 큰 작업 | step 설계·실행 준비 |
| `/rollback 문제` | 배포 후 사고 | 마지막 배포 되돌리고 새 버전으로 재배포 |

### 에이전트 (명령어가 알아서 부름. "architect 로 설계해줘" 처럼 직접 불러도 됨)
| 이름 | 역할 | 코드 수정 |
|------|------|---------|
| `architect` | 설계안·단계 쪼개기·ADR 제안 | ✗ |
| `tester` | 자동 테스트 작성·실행, 수동 점검 항목 | 테스트 파일만 |
| `debugger` | 근본 원인 추적 | ✗ |
| `reviewer` | 버그·규칙 위반 검토 | ✗ |
| `privacy-guard` | 개인정보·비밀키·동의·RLS 점검 | ✗ |
| `ui-checker` | 디자인 표준·버튼 단어·4가지 상태 | ✗ |
| `docs-keeper` | 코드 ↔ 문서 동기화 | 문서만 |

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

### 훅 (항상 켜져 있음)
| 때 | 하는 일 |
|----|--------|
| Claude Code 켤 때 | 다른 PC 에서 올린 변경이 있으면 `git pull` 하라고 알림 |
| 명령 실행 전 | 폴더 통째 삭제·강제 push·작업 버리기 등 되돌릴 수 없는 명령 차단 |
| 커밋 직전 | `.env`·키 파일·5MB 이상 파일이 섞여 있으면 차단 |
| 파일 쓰기 전 | API 키·service_role 키가 코드에 들어가면 차단 |
| 파일 쓴 직후 | js 문법·json 형식·html 태그 짝 검사 → 틀리면 즉시 고치게 |
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
/status           ← 오늘 할 일 확인
/feature …        ← 또는 /fix …
/ship             ← 폰 점검표 확인 후 배포
```

## 6. 기존 앱 가져오기 (예: posture-check)
```powershell
cd $HOME\Documents\harness_framework
powershell -ExecutionPolicy Bypass -File scripts\adopt.ps1 $HOME\Documents\posture-check
```
스크립트가 알려 주는 `cd` 와 `claude` 를 입력한 뒤 `/adopt 아요바디요 체형 측정 앱`.
`/adopt` 가 코드를 읽어 문서를 채우고, 표준과 다른 점(🔴 비밀키·버전 불일치 등)을 BACKLOG 에 넣는다. 그다음부터 `/feature` `/fix` `/ship` 을 그대로 쓴다.

## 7. 큰 작업 실행기 (`/harness` + execute.py)
1. `/harness` → 논의 → "구현 계획 짜 줘" → 승인 → `phases/` 생성
2. `git add -A && git commit -m "docs: 구현 계획"` (실행기는 저장 안 된 변경이 있으면 멈춤)
3. `python scripts/execute.py 0-mvp` (`--push` 붙이면 끝나고 push)
4. 결과: `phases/0-mvp/index.json` 의 `status`. `error`/`blocked` 는 원인 해결 → `"pending"` 으로 바꾸고 재실행
5. 끝나면 `git checkout main` → `git merge feat-0-mvp` → `/ship`

실행기 사전 점검(빈칸·미커밋·claude 설치)을 건너뛰려면 `--skip-preflight`. 한 step 이 30분을 넘기면 자동 중단되어 `error` 로 기록된다.

## 7-1. 틀 자체를 고쳤을 때
틀(`harness_framework`)의 훅·명령·스킬을 고쳤다면 → 틀 폴더에서 커밋·push → 각 앱 폴더에 `scripts\update-harness.ps1 앱경로` 로 반영. 문서와 코드는 건드리지 않고 도구만 바뀐다.

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
