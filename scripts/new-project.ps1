<#
이 하네스 틀을 Documents\{이름} 으로 복사하고, git 기록(.git)은 빼고, 새 git 저장소로 시작한다.

사용법:  powershell -ExecutionPolicy Bypass -File scripts\new-project.ps1 my-app
#>
param(
    [Parameter(Mandatory = $true)][string]$Name
)
$ErrorActionPreference = "Stop"

if ($Name -notmatch '^[\w.-]+$') {
    Write-Error "프로젝트 이름에는 영문/숫자/한글, -, _, . 만 쓸 수 있습니다: $Name"
}

$template = Split-Path -Parent $PSScriptRoot
$dest = Join-Path ([Environment]::GetFolderPath("MyDocuments")) $Name

# 이미 있는 폴더를 덮어쓰면 기존 작업이 날아가므로 멈춘다
if (Test-Path $dest) {
    Write-Error "이미 있는 폴더입니다: $dest"
}

New-Item -ItemType Directory -Path $dest | Out-Null
Get-ChildItem -Path $template -Force |
    Where-Object { $_.Name -ne ".git" } |
    Copy-Item -Destination $dest -Recurse -Force

git -C $dest init
if ($LASTEXITCODE -ne 0) { Write-Error "git init 실패" }

Write-Host ""
Write-Host "완료: $dest"
Write-Host "다음 단계: START_HERE.md 3번 표의 빈칸을 채우세요."
