<#
이 하네스 틀을 Documents\{이름} 으로 복사하고, git 기록(.git)은 빼고, 새 git 저장소(main 브랜치)로 시작한다.

사용법:  powershell -ExecutionPolicy Bypass -File scripts\new-project.ps1 my-app
#>
param(
    [Parameter(Mandatory = $true)][string]$Name
)
$ErrorActionPreference = "Stop"

if ($Name -notmatch '^[\w.-]+$') {
    Write-Error "프로젝트 이름에는 영문/숫자, -, _, . 만 쓸 수 있습니다 (한글·공백 불가): $Name"
}

$template = Split-Path -Parent $PSScriptRoot
$docs = [Environment]::GetFolderPath("MyDocuments")   # OneDrive 로 옮겨진 '문서' 폴더도 따라간다
$dest = Join-Path $docs $Name

# 이미 있는 폴더를 덮어쓰면 기존 작업이 날아가므로 멈춘다
if (Test-Path $dest) {
    Write-Error "이미 있는 폴더입니다: $dest"
}

# 틀에만 필요한 것(테스트 캐시, 실행 기록, 로컬 설정)은 복사하지 않는다
$exclude = @(".git", ".pytest_cache", "__pycache__", "phases", ".mcp.json", ".env", "node_modules", ".shots")

New-Item -ItemType Directory -Path $dest | Out-Null
Get-ChildItem -Path $template -Force |
    Where-Object { $exclude -notcontains $_.Name } |
    Copy-Item -Destination $dest -Recurse -Force
Get-ChildItem -Path $dest -Recurse -Force -Directory |
    Where-Object { $_.Name -in @("__pycache__", ".pytest_cache") } |
    Remove-Item -Recurse -Force

# 틀 자체에만 쓰는 것은 새 앱에 넘기지 않는다: 이 PC 권한 설정(push 허용 등), 틀의 계획서, 틀의 인수인계
Remove-Item (Join-Path $dest ".claude\settings.local.json") -Force -ErrorAction SilentlyContinue
Get-ChildItem (Join-Path $dest "docs\PLANS") -Filter "20*.md" -ErrorAction SilentlyContinue | Remove-Item -Force
$blankHandoff = @'
# 인수인계 (HANDOFF)

> `/handoff` 가 쓰는 문서. 대화를 새로 시작하거나 다른 PC 로 옮길 때 **이 문서 한 장**으로 이어간다 (긴 대화를 다시 읽지 않아 토큰을 아낌).
> 항상 **최신 상태 하나만** 둔다. 지난 기록은 CHANGELOG·docs/PLANS·git log 에 있다. 회원 실명·연락처는 쓰지 않는다.

상태: 없음
갱신: -

## 지금 하던 일
(없음)

## 다음 할 일 (순서대로, 바로 입력할 명령 포함)
1. (없음)

## 이번에 끝낸 것
- (없음)

## 정해진 것 / 결정 대기
- (없음)

## 주의할 점
- (없음)

## 관련 파일
- (없음)
'@
[IO.File]::WriteAllText((Join-Path $dest "docs\HANDOFF.md"), $blankHandoff + "`n", (New-Object Text.UTF8Encoding $false))

git -C $dest init -b main
if ($LASTEXITCODE -ne 0) {
    # 오래된 git 은 -b 를 모른다
    git -C $dest init
    git -C $dest checkout -b main
}
if ($LASTEXITCODE -ne 0) { Write-Error "git init 실패" }

Write-Host ""
Write-Host "완료: $dest  (브랜치 main)"
Write-Host ""
Write-Host "다음 두 줄을 그대로 입력하세요:"
Write-Host "  cd `"$dest`""
Write-Host "  claude"
Write-Host "그리고 Claude Code 에서:  /start 만들 앱 한 줄 설명"
