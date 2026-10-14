"""PreToolUse 훅(Write/Edit): 비밀키가 코드 파일에 들어가는 것을 막는다.

비밀키는 .env 파일(이미 .gitignore 대상)에만 둬야 한다. 코드에 들어가면 GitHub에 그대로 올라가
누구나 볼 수 있게 된다. 종료코드 2 = 차단.

주의: Supabase의 anon(publishable) 키는 원래 공개용이라 막지 않는다. service_role 키만 막는다.
"""

import base64
import json
import re
import sys
from pathlib import Path

PATTERNS = [
    (r"sk-(ant-|proj-)?[A-Za-z0-9_-]{20,}", "OpenAI/Anthropic API 키"),
    (r"AKIA[0-9A-Z]{16}", "AWS 액세스 키"),
    (r"gh[pousr]_[A-Za-z0-9]{36,}", "GitHub 토큰"),
    (r"AIza[0-9A-Za-z_-]{35}", "Google API 키"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "개인 키(Private key)"),
    (r"sb_secret_[A-Za-z0-9_-]{20,}", "Supabase secret 키"),
]
JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.(eyJ[A-Za-z0-9_-]{10,})\.[A-Za-z0-9_-]{10,}")
SAFE_FILES = re.compile(r"(^|[\\/])\.env(\.[\w-]+)?$")  # .env, .env.local 등은 허용


def is_service_role(payload_b64: str) -> bool:
    try:
        raw = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4))
        return '"service_role"' in raw.decode("utf-8", "ignore")
    except Exception:
        return False


def find_secret(text: str):
    for pattern, label in PATTERNS:
        if re.search(pattern, text):
            return label
    for m in JWT.finditer(text):
        if is_service_role(m.group(1)):
            return "Supabase service_role 키"
    return None


sys.stdin.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
path = tool_input.get("file_path", "")
if SAFE_FILES.search(path) and not Path(path).name.endswith(".example"):
    sys.exit(0)

texts = [tool_input.get("content", ""), tool_input.get("new_string", "")]
texts += [e.get("new_string", "") for e in tool_input.get("edits", [])]
label = find_secret("\n".join(t for t in texts if t))
if label:
    print(f"BLOCKED: {Path(path).name}에 {label}로 보이는 값이 들어가려 해서 막았습니다.\n"
          f"비밀키는 .env 파일에 넣고 코드에서는 환경변수로 읽으세요.", file=sys.stderr)
    sys.exit(2)
