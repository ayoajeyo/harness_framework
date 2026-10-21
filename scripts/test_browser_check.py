"""scripts/browser_check.py 점검 — 시나리오 검사, 개인정보 차단, (가능하면) 실제 브라우저 실행."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("browser_check", ROOT / "scripts" / "browser_check.py")
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)


def test_page_is_required():
    assert any("page" in e for e in bc.validate({}))
    assert bc.validate({"page": "index.html"}) == []


def test_each_step_has_exactly_one_action():
    errs = bc.validate({"page": "x.html", "steps": [{"click": "#a", "wait": 1}, {}]})
    assert len(errs) == 2


def test_download_needs_file_name():
    assert bc.validate({"page": "x.html", "steps": [{"download": "#b"}]})
    assert bc.validate({"page": "x.html", "steps": [{"download": "#b", "save": "a.xlsx"}]}) == []


def test_seed_shape_and_route_file():
    assert bc.validate({"page": "x.html", "seed": {"db": "d"}})
    assert bc.validate({"page": "x.html", "seed": {"db": "d", "stores": {"members": []}}}) == []
    assert bc.validate({"page": "x.html", "route": {"**/x.js": "없는-파일.js"}})


def test_fake_phone_ok_real_like_phone_blocked():
    assert bc.pii_problems('{"phone": "010-0000-0000", "name": "홍길동"}', names_file="없음.txt") == []
    assert bc.pii_problems('{"phone": "010-1234-5678"}', names_file="없음.txt")


def test_names_in_local_list_blocked(tmp_path):
    nf = tmp_path / "names.txt"
    nf.write_text("# 실제 회원 이름 (PC 에만)\n김가짜\n", encoding="utf-8")
    assert bc.pii_problems('{"name": "김가짜"}', names_file=nf)
    assert bc.pii_problems('{"name": "홍길동"}', names_file=nf) == []


def test_pii_scenario_is_not_run(tmp_path, capsys):
    sc = tmp_path / "s.json"
    sc.write_text(json.dumps({"page": "index.html", "steps": [{"eval": "'010-9876-5432'"}]}), encoding="utf-8")
    assert bc.main([str(sc)]) == bc.EXIT_PII


def test_real_run_on_styleguide(tmp_path):
    pytest.importorskip("playwright.sync_api")
    page = "design-system/styleguide.html"
    if not (ROOT / page).exists():
        pytest.skip("견본 페이지 없음")
    sc = tmp_path / "s.json"
    sc.write_text(json.dumps({"page": page, "steps": [{"eval": "document.title.length > 0", "expect": True}]}), encoding="utf-8")
    code = bc.main([str(sc), "--out", str(tmp_path)])
    if code == bc.EXIT_NO_PLAYWRIGHT:
        pytest.skip("브라우저 본체 없음")
    assert code == 0


def test_route_serves_local_file(tmp_path):
    pytest.importorskip("playwright.sync_api")
    page = "design-system/styleguide.html"
    if not (ROOT / page).exists():
        pytest.skip("견본 페이지 없음")
    sc = tmp_path / "s.json"
    # 없는 CDN 주소 요청을 저장소 안 파일로 대신 넘겨주는지 (외부 라이브러리를 못 받는 PC·클라우드용)
    sc.write_text(json.dumps({"page": page, "route": {"**/does-not-exist.js": page},
        "steps": [{"eval": "fetch('https://cdn.example.invalid/does-not-exist.js').then(r => r.ok)", "expect": True}]}), encoding="utf-8")
    code = bc.main([str(sc), "--out", str(tmp_path)])
    if code == bc.EXIT_NO_PLAYWRIGHT:
        pytest.skip("브라우저 본체 없음")
    assert code == 0
