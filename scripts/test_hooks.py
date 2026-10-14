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
])
def test_blocks_dangerous(cmd):
    r = run_hook("block_dangerous.py", json.dumps({"tool_input": {"command": cmd}}, ensure_ascii=False))
    assert r.returncode == 2
    assert "BLOCKED" in r.stderr.decode("utf-8")


@pytest.mark.parametrize("cmd", ["ls -la", "git push origin main", "rm file.txt", "echo 한글"])
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
