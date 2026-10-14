"""PreToolUse 훅: 위험한 셸 명령을 막는다.

Claude Code는 도구 입력을 stdin JSON으로 넘긴다. 종료코드 2 = 차단(stderr가 Claude에게 전달됨).
"""

import json
import re
import sys

DANGEROUS = re.compile(
    r"rm\s+-(rf|fr)\b|git\s+push\s+.*(--force|-f\b)|git\s+reset\s+--hard|DROP\s+TABLE",
    re.IGNORECASE,
)

# Windows 기본 cp949면 한글이 깨지거나, 읽다 죽어서(종료코드 1 = 통과) 차단이 풀린다
sys.stdin.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
if DANGEROUS.search(command):
    print(f"BLOCKED: 위험한 명령어가 감지되었습니다: {command}", file=sys.stderr)
    sys.exit(2)
