""".claude/hooks 스크립트 테스트. 실제 명령은 실행하지 않고 JSON만 넘겨 본다."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).parent.parent / ".claude" / "hooks"


def run_hook(name, stdin, env=None):
    return subprocess.run([sys.executable, str(HOOKS / name)], input=stdin.encode("utf-8"),
                          capture_output=True, env={**os.environ, **(env or {})})


@pytest.mark.parametrize("cmd", [
    "rm -rf build", "rm -fr x", "git push --force origin main", "git push origin main -f",
    "git reset --hard HEAD~1", "drop table users", "echo 한글 && rm -rf /",
    "Remove-Item -Recurse -Force .\\build", "Remove-Item C:\\x -Force -Recurse",
    "rmdir /s /q build", "rd /S dist", "del /s *.js", "git clean -fd", "format d:",
])
def test_blocks_dangerous(cmd):
    r = run_hook("block_dangerous.py", json.dumps({"tool_input": {"command": cmd}}, ensure_ascii=False))
    assert r.returncode == 2
    assert "BLOCKED" in r.stderr.decode("utf-8")


@pytest.mark.parametrize("cmd", ["ls -la", "git push origin main", "rm file.txt", "echo 한글",
                                 "Remove-Item old.txt", "git status", "python -m http.server"])
def test_allows_safe(cmd):
    r = run_hook("block_dangerous.py", json.dumps({"tool_input": {"command": cmd}}, ensure_ascii=False))
    assert r.returncode == 0


def test_stop_passes_without_package_json(tmp_path):
    r = run_hook("stop_check.py", "{}", {"CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert r.returncode == 0 and r.stdout == b"" and r.stderr == b""


@pytest.mark.parametrize("lint,code", [("echo ok", 0), ("node -e process.exit(3)", 1)])
def test_stop_runs_npm_scripts(tmp_path, lint, code):
    scripts = {"lint": lint, "build": "echo ok", "test": "echo ok"}
    (tmp_path / "package.json").write_text(json.dumps({"scripts": scripts}), encoding="utf-8")
    r = run_hook("stop_check.py", "{}", {"CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert r.returncode == code


# --- secret_guard.py ---------------------------------------------------------

import base64


def jwt(payload: str) -> str:
    enc = lambda t: base64.urlsafe_b64encode(t.encode()).decode().rstrip("=")
    return f"{enc('{\"alg\":\"HS256\",\"typ\":\"JWT\"}')}.{enc(payload)}.abcdefghijklmnopqrstuvwxyz012345"


def write(path, content, tool="content"):
    key = "new_string" if tool == "edit" else "content"
    return run_hook("secret_guard.py", json.dumps({"tool_input": {"file_path": path, key: content}},
                                                  ensure_ascii=False))


@pytest.mark.parametrize("content", [
    'const KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz123456"',
    "aws = 'AKIAABCDEFGHIJKLMNOP'",
    "token: ghp_" + "a" * 36,
    "-----BEGIN RSA PRIVATE KEY-----",
    "const s = '" + "sb_secret_" + "x" * 30 + "'",
])
def test_secret_blocked(content):
    r = write("js/app.js", content)
    assert r.returncode == 2
    assert "BLOCKED" in r.stderr.decode("utf-8")


def test_service_role_jwt_blocked():
    token = jwt('{"iss":"supabase","role":"service_role"}')
    assert write("js/config.js", f"const k = '{token}'").returncode == 2


def test_anon_jwt_allowed():
    token = jwt('{"iss":"supabase","role":"anon"}')
    assert write("js/config.js", f"const k = '{token}'").returncode == 0


def test_secret_in_edit_blocked():
    assert write("js/app.js", "x = 'sk-ant-abcdefghijklmnopqrstuvwxyz'", tool="edit").returncode == 2


def test_secret_in_multiedit_blocked():
    payload = {"tool_input": {"file_path": "a.js", "edits": [{"new_string": "AKIAABCDEFGHIJKLMNOP"}]}}
    assert run_hook("secret_guard.py", json.dumps(payload)).returncode == 2


@pytest.mark.parametrize("path", [".env", ".env.local", "C:\\proj\\.env", "/home/u/p/.env.production"])
def test_env_files_allowed(path):
    assert write(path, "OPENAI_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz123456").returncode == 0


def test_env_example_with_real_key_blocked():
    assert write(".env.example", "KEY=sk-proj-abcdefghijklmnopqrstuvwxyz123456").returncode == 2


def test_plain_code_allowed():
    assert write("js/app.js", "const name = '홍길동'; // 한글 주석").returncode == 0


# --- session_start.py --------------------------------------------------------

def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def test_session_start_silent_outside_git(tmp_path):
    r = run_hook("session_start.py", "{}", {"CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert r.returncode == 0 and r.stdout == b""


def test_session_start_reports_uncommitted(tmp_path):
    git(tmp_path, "init", "-q")
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    r = run_hook("session_start.py", "{}", {"CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert r.returncode == 0
    assert "1개" in r.stdout.decode("utf-8")


def test_session_start_reports_behind(tmp_path):
    remote, local, other = tmp_path / "remote.git", tmp_path / "local", tmp_path / "other"
    git(tmp_path, "init", "-q", "--bare", str(remote))
    git(tmp_path, "clone", "-q", str(remote), str(other))
    for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
        git(other, "config", k, v)
    (other / "f.txt").write_text("1", encoding="utf-8")
    git(other, "add", ".")
    git(other, "commit", "-qm", "c1")
    git(other, "push", "-q", "origin", "HEAD")
    git(tmp_path, "clone", "-q", str(remote), str(local))  # 병원 PC: 여기까지 받은 상태
    (other / "f.txt").write_text("2", encoding="utf-8")
    git(other, "commit", "-qam", "c2")
    git(other, "push", "-q", "origin", "HEAD")             # 집 PC에서 새로 올림
    r = run_hook("session_start.py", "{}", {"CLAUDE_PROJECT_DIR": str(local)})
    out = r.stdout.decode("utf-8")
    assert r.returncode == 0
    assert "git pull" in out and "1개" in out
