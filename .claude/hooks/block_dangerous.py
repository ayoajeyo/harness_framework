"""PreToolUse 훅: 되돌릴 수 없는 위험한 셸 명령을 막는다.

Claude Code는 도구 입력을 stdin JSON으로 넘긴다. 종료코드 2 = 차단(stderr가 Claude에게 전달됨).
Bash뿐 아니라 PowerShell 계열의 같은 뜻 명령도 함께 막는다.
"""

import json
import re
import sys

DANGEROUS = re.compile(
    r"|".join([
        r"rm\s+-(rf|fr)\b",                                  # 폴더 통째 삭제 (bash)
        r"Remove-Item\b(?=.*-Recurse)(?=.*-Force)",          # 폴더 통째 삭제 (PowerShell)
        r"\b(rmdir|rd)\s+/s\b",                              # 폴더 통째 삭제 (cmd)
        r"\bdel\s+/s\b",                                     # 하위 파일 일괄 삭제 (cmd)
        r"git\s+push\s+.*(--force|-f\b)",                    # GitHub 기록 덮어쓰기
        r"git\s+reset\s+--hard",                             # 작업 내용 버리기
        r"git\s+clean\s+-\w*f",                              # 저장 안 된 새 파일 삭제
        r"DROP\s+(TABLE|DATABASE)",                          # DB 삭제
        r"\bformat\s+[a-z]:",                                # 드라이브 포맷
    ]),
    re.IGNORECASE,
)

# Windows 기본 cp949면 한글이 깨지거나, 읽다 죽어서(종료코드 1 = 통과) 차단이 풀린다
sys.stdin.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
if DANGEROUS.search(command):
    print(f"BLOCKED: 되돌릴 수 없는 위험한 명령이라 막았습니다: {command}\n"
          f"꼭 필요하면 사용자에게 이유를 설명하고 직접 실행하도록 안내하세요.", file=sys.stderr)
    sys.exit(2)
