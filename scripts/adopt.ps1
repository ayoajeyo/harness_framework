<#
이미 만든 앱(기존 저장소)에 하네스 도구와 문서 틀을 넣는다. 기존 파일은 덮어쓰지 않는다.

사용법:  powershell -ExecutionPolicy Bypass -File scripts\adopt.ps1 C:\Users\USER\Documents\posture-check
그다음 그 폴더에서 claude 를 켜고 /adopt 를 입력한다.
이미 하네스가 있는 앱에 새 버전을 반영하려면 update-harness.ps1 을 쓴다.
#>
param(
    [Parameter(Mandatory = $true)][string]$Target
)
$ErrorActionPreference = "Stop"
$template = Split-Path -Parent $PSScriptRoot

if (-not (Test-Path $Target)) { Write-Error "폴더가 없습니다: $Target" }
if (-not (Test-Path (Join-Path $Target ".git"))) { Write-Error "git 저장소가 아닙니다: $Target  (먼저 git init 또는 clone)" }

$copied = @(); $skipped = @()
function Copy-IfMissing($rel) {
    $src = Join-Path $template $rel
    $dst = Join-Path $Target $rel
    if (Test-Path $dst) { $script:skipped += $rel; return }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
    Copy-Item $src $dst -Recurse
    $script:copied += $rel
}

# .claude 는 하위 항목 단위로 (기존 앱에 .claude\settings.local.json 만 있어도 도구가 들어가게)
foreach ($sub in @("settings.json", "hooks", "commands", "agents", "skills")) { Copy-IfMissing (Join-Path ".claude" $sub) }
foreach ($rel in @("scripts\execute.py", "scripts\test_execute.py", "scripts\test_hooks.py", "scripts\test_structure.py", "scripts\screenshot.py", "scripts\test_screenshot.py", "scripts\app_capture.py", "scripts\test_app_capture.py", "scripts\browser_check.py", "scripts\test_browser_check.py", "scripts\update-harness.ps1", ".env.example", ".mcp.json.example", "THIRD_PARTY_NOTICES.md")) { Copy-IfMissing $rel }
foreach ($doc in Get-ChildItem (Join-Path $template "docs") -Filter *.md) { Copy-IfMissing ("docs\" + $doc.Name) }
Copy-IfMissing "docs\PLANS\README.md"
Copy-IfMissing "design-system"   # 참고용 견본. 자기 CSS 가 있는 앱에는 걸지 않는다 (clean-ui 스킬 "기존 앱")

# CLAUDE.md 가 이미 있으면 옆에 참고본으로
if (Test-Path (Join-Path $Target "CLAUDE.md")) {
    Copy-Item (Join-Path $template "CLAUDE.md") (Join-Path $Target "CLAUDE.harness.md")
    $copied += "CLAUDE.harness.md  (기존 CLAUDE.md 와 합치세요 — /adopt 가 도와줌)"
} else { Copy-IfMissing "CLAUDE.md" }

# .gitignore 에 비밀 파일 규칙 보강
$gi = Join-Path $Target ".gitignore"
$rules = @(".env", ".env.*", "!.env.example", "*.key", "*.pem", "*.jks", "*.keystore", "*.aab", "*.apk", ".mcp.json", ".claude/pii-names.local.txt", "phases/**/step*-output.json", "__pycache__/", ".pytest_cache/", ".shots/", ".archify/")
$existing = if (Test-Path $gi) { Get-Content $gi } else { @() }
$add = $rules | Where-Object { $existing -notcontains $_ }
if ($add) { Add-Content $gi ("`n# harness`n" + ($add -join "`n")); $copied += ".gitignore (규칙 " + $add.Count + "개 추가)" }

Write-Host ""
Write-Host "넣은 것:";   $copied  | ForEach-Object { Write-Host "  + $_" }
Write-Host "이미 있어서 건너뜀:"; $skipped | ForEach-Object { Write-Host "  = $_" }
Write-Host ""
Write-Host "다음 두 줄을 입력하세요:"
Write-Host "  cd `"$Target`""
Write-Host "  claude"
Write-Host "그리고 Claude Code 에서:  /adopt 앱 이름"
