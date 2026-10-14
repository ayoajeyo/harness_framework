"""Stop 훅: package.json이 있을 때만 lint → build → test를 실행한다. 없으면 조용히 통과."""

import os
import subprocess
import sys
from pathlib import Path

sys.stderr.reconfigure(encoding="utf-8")  # Windows 기본 cp949면 한글 메시지가 깨진다
root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
if not (root / "package.json").exists():
    sys.exit(0)

for script in ("lint", "build", "test"):
    # shell=True: Windows에서 npm은 npm.cmd라서 셸을 거쳐야 실행된다
    r = subprocess.run(f"npm run {script}", shell=True, cwd=root,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"npm run {script} 실패:\n{r.stdout[-2000:]}{r.stderr[-2000:]}", file=sys.stderr)
        sys.exit(1)
