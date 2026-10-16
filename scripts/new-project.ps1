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
