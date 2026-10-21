"""브라우저 점검 — 시나리오(JSON) 대로 앱을 실제 브라우저에서 움직여 보고, 됐는지 안 됐는지 알려 준다.

자동 테스트(node --test)는 계산만 본다. "버튼을 누르면 파일이 정말 내려받아지나", "예전 기록이 있어도
오류 없이 열리나" 처럼 화면·저장소가 함께 움직이는 기능은 이 스크립트로 확인한다.
`browser-check` 스킬이 언제·어떻게 쓰는지 설명한다.

사용법:
    python scripts/browser_check.py tests/browser/내보내기.json
    python scripts/browser_check.py tests/browser/내보내기.json --width 390

시나리오 예 (모든 칸 선택):
    {
      "page": "index.html",                      # 저장소 안 파일(로컬 서버로 연다) 또는 http(s) 주소
      "hash": "#members",
      "localStorage": {"app_admin": "1"},        # 첫 화면을 연 뒤 넣고 다시 연다
      "seed": {"db": "앱-저장소-이름", "stores": {"members": [{"id": "m1", "name": "홍길동"}]}},
      "route": {"**/exceljs.min.js": "vendor/exceljs.min.js"},   # 외부(CDN) 파일을 저장소 안 파일로 대신
      "hide": ["#authGate"],                     # 테스트를 가리는 로그인 화면 등
      "steps": [
        {"click": "#btnOpen"},
        {"wait": 500},
        {"waitText": "보관된 기록"},
        {"eval": "document.querySelectorAll('.row').length", "expect": 3},
        {"download": "#btnSave", "save": "내보내기.xlsx"},
        {"shot": "결과"}
      ]
    }

끝나는 번호: 0 = 모두 통과, 2 = 실패한 단계·스크립트 오류 있음, 3 = Playwright 없음,
4 = 페이지를 열지 못함, 5 = 시나리오에 실제 개인정보로 보이는 값(실행하지 않음).
결과 파일(사진·내려받은 파일)은 .shots/ 에 저장한다(git 에 안 올라감).

서비스워커는 항상 막는다(예전 파일이 캐시로 보여 결과가 틀리는 것 방지).
처음 한 번 설치(PC 마다): python -m pip install playwright  /  python -m playwright install chromium
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screenshot as S  # noqa: E402  같은 로컬 서버·주소 규칙을 쓴다

EXIT_FAIL = 2
EXIT_NO_PLAYWRIGHT = 3
EXIT_OPEN_FAILED = 4
EXIT_PII = 5
STEP_KEYS = ("click", "wait", "waitText", "eval", "download", "shot")
# 010-0000-0000 처럼 0 만 있는 번호만 가짜로 본다
PHONE_RE = re.compile(r"01[016789][-\s]?(\d{3,4})[-\s]?(\d{4})")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="시나리오(JSON) 대로 브라우저에서 앱을 점검")
    p.add_argument("scenario", help="시나리오 JSON 파일 경로")
    p.add_argument("--width", type=int, default=390)
    p.add_argument("--height", type=int, default=844)
    p.add_argument("--out", default=".shots", help="사진·내려받은 파일 저장 폴더 (기본 .shots)")
    return p.parse_args(argv)


def load_scenario(path):
    p = Path(path)
    if not p.is_absolute():
        p = (Path.cwd() / p) if (Path.cwd() / p).exists() else ROOT / p
    text = p.read_text(encoding="utf-8")
    return json.loads(text), text


def validate(sc):
    """시나리오 모양 검사 → 문제 목록(빈 목록이면 정상)."""
    errs = []
    if not isinstance(sc, dict):
        return ["시나리오는 { } 로 감싼 JSON 이어야 합니다"]
    if not sc.get("page"):
        errs.append('"page" 가 없습니다 (예: "index.html")')
    seed = sc.get("seed")
    if seed is not None:
        if not isinstance(seed, dict) or not seed.get("db") or not isinstance(seed.get("stores"), dict):
            errs.append('"seed" 는 {"db": 이름, "stores": {저장소: [자료…]}} 모양이어야 합니다')
    for i, st in enumerate(sc.get("steps") or []):
        keys = [k for k in STEP_KEYS if k in (st or {})]
        if len(keys) != 1:
            errs.append(f"{i + 1}번째 단계: {', '.join(STEP_KEYS)} 중 하나만 적어 주세요")
        if "download" in (st or {}) and not st.get("save"):
            errs.append(f"{i + 1}번째 단계: download 에는 저장할 파일 이름 \"save\" 가 필요합니다")
    for pat, local in (sc.get("route") or {}).items():
        if not (ROOT / local).exists():
            errs.append(f"route 대신 쓸 파일이 저장소에 없습니다: {local}")
    return errs


def pii_problems(text, names_file=None):
    """시나리오 글에 실제 개인정보로 보이는 값이 있으면 목록으로. (가짜: 홍길동, 010-0000-0000)"""
    found = []
    for m in PHONE_RE.finditer(text):
        if m.group(1).strip("0") or m.group(2).strip("0"):
            found.append(f"전화번호 같은 값: {m.group(0)} (가짜 010-0000-0000 만 쓰세요)")
    nf = Path(names_file) if names_file else ROOT / ".claude" / "pii-names.local.txt"
    if nf.exists():
        for line in nf.read_text(encoding="utf-8").splitlines():
            n = line.strip()
            if n and not n.startswith("#") and n in text:
                found.append("실제 회원 이름 목록(.claude/pii-names.local.txt)에 있는 이름이 들어 있습니다")
                break
    return found


SEED_JS = """async (seed) => {
  const db = await new Promise((ok, no) => { const q = indexedDB.open(seed.db); q.onsuccess = () => ok(q.result); q.onerror = () => no(q.error); });
  const missing = Object.keys(seed.stores).filter((s) => !db.objectStoreNames.contains(s));
  if (missing.length) { db.close(); return "없는 저장소: " + missing.join(", "); }
  for (const [store, rows] of Object.entries(seed.stores)) {
    await new Promise((ok, no) => { const t = db.transaction(store, "readwrite"); rows.forEach((r) => t.objectStore(store).put(r)); t.oncomplete = ok; t.onerror = () => no(t.error); });
  }
  db.close(); return "";
}"""


def run(args):
    try:
        sc, text = load_scenario(args.scenario)
    except (OSError, json.JSONDecodeError) as e:
        print(f"시나리오를 읽지 못했습니다: {e}", file=sys.stderr)
        return EXIT_FAIL
    errs = validate(sc)
    if errs:
        print("시나리오 문제:\n- " + "\n- ".join(errs), file=sys.stderr)
        return EXIT_FAIL
    pii = pii_problems(text)
    if pii:
        print("실행하지 않았습니다 — 시나리오에는 가짜 정보만 씁니다:\n- " + "\n- ".join(pii), file=sys.stderr)
        return EXIT_PII
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(S.INSTALL_HELP, file=sys.stderr)
        return EXIT_NO_PLAYWRIGHT

    out_dir = Path(args.out) if Path(args.out).is_absolute() else ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    server, base = (None, "")
    if not re.match(r"https?://", sc["page"]):
        server, base = S.start_server(ROOT)
    url = S.resolve_url(sc["page"], base) + (sc.get("hash") or "")
    results, errors = [], []
    try:
        with sync_playwright() as pw:
            try:
                browser = pw.chromium.launch()
            except PlaywrightError as e:
                print(S.INSTALL_HELP + f"\n({str(e).splitlines()[0][:120]})", file=sys.stderr)
                return EXIT_NO_PLAYWRIGHT
            try:
                ctx = browser.new_context(viewport={"width": args.width, "height": args.height}, is_mobile=True, has_touch=True,
                                          locale="ko-KR", service_workers="block", accept_downloads=True)
                def serve_local(path):   # route 콜백은 (route, request) 두 개를 받는다 — 파일 경로는 바깥에서 묶어 둔다
                    return lambda route, _req=None: route.fulfill(path=path)
                for pat, local in (sc.get("route") or {}).items():
                    ctx.route(pat, serve_local(str(ROOT / local)))
                page = ctx.new_page()
                page.on("pageerror", lambda e: errors.append(f"스크립트 오류: {e}"))
                try:
                    page.goto(url, wait_until="load", timeout=30000)
                    if sc.get("localStorage") or sc.get("seed"):
                        page.evaluate("(o) => { for (const k in o) localStorage.setItem(k, o[k]); }", sc.get("localStorage") or {})
                        if sc.get("seed"):
                            msg = page.evaluate(SEED_JS, sc["seed"])
                            if msg:
                                results.append((False, f"자료 넣기: {msg} (앱이 저장소를 만든 뒤인지 확인)"))
                        page.reload(wait_until="load")
                except PlaywrightError as e:
                    print(f"페이지를 열지 못했습니다: {url}\n({str(e).splitlines()[0][:160]})", file=sys.stderr)
                    return EXIT_OPEN_FAILED
                for sel in sc.get("hide") or []:
                    page.evaluate("(s) => document.querySelectorAll(s).forEach((e) => { e.style.display = 'none'; })", sel)
                for i, st in enumerate(sc.get("steps") or []):
                    label = f"{i + 1}. " + json.dumps(st, ensure_ascii=False)[:80]
                    try:
                        if "click" in st:
                            # 다른 요소가 덮고 있어도 누르도록 화면 안에서 직접 click()
                            ok = page.evaluate("(s) => { const e = document.querySelector(s); if (!e) return false; e.click(); return true; }", st["click"])
                            results.append((ok, label + ("" if ok else " — 요소를 못 찾음")))
                        elif "wait" in st:
                            page.wait_for_timeout(int(st["wait"])); results.append((True, label))
                        elif "waitText" in st:
                            page.get_by_text(st["waitText"]).first.wait_for(timeout=int(st.get("timeout", 15000)))
                            results.append((True, label))
                        elif "eval" in st:
                            v = page.evaluate(st["eval"])
                            ok = ("expect" not in st) or v == st["expect"]
                            results.append((ok, label + f" → {json.dumps(v, ensure_ascii=False)[:120]}" + ("" if ok else f" (기대: {st['expect']})")))
                        elif "download" in st:
                            with page.expect_download(timeout=int(st.get("timeout", 120000))) as d:
                                page.evaluate("(s) => document.querySelector(s).click()", st["download"])
                            dest = out_dir / Path(st["save"]).name
                            d.value.save_as(str(dest))
                            results.append((True, label + f" → {dest.relative_to(ROOT) if dest.is_relative_to(ROOT) else dest} ({dest.stat().st_size:,} bytes)"))
                        elif "shot" in st:
                            dest = out_dir / f"{S.slug(st['shot'])}-{args.width}.png"
                            page.screenshot(path=str(dest)); results.append((True, label + f" → {dest.name}"))
                    except (PlaywrightError, TypeError, ValueError) as e:
                        results.append((False, label + f" — {str(e).splitlines()[0][:140]}"))
            finally:
                browser.close()
    finally:
        if server:
            server.shutdown(); server.server_close()

    for ok, msg in results:
        print(("통과 " if ok else "실패 ") + msg)
    for e in errors[:10]:
        print("- " + e)
    bad = [r for r in results if not r[0]]
    print(f"결과: {len(results) - len(bad)}/{len(results)} 단계 통과" + (f", 스크립트 오류 {len(errors)}건" if errors else ""))
    return EXIT_FAIL if bad or errors else 0


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    return run(parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
