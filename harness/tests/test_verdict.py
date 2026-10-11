"""verdict.py 검증 (harness/verification.md).

게이트 ID마다 위반 샘플을 하나씩 만들어 해당 ID가 검출되는지, 통과 샘플은 위반 0건인지 확인한다.
위반 샘플은 통과 샘플을 한 군데만 고쳐서 만든다 (파일 26개를 따로 두지 않는다).
실행: python3 -m unittest discover -s harness/tests -v
"""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))
import verdict  # noqa: E402

SLUG = "sample-screen"
CHECKLIST = ["실제 업무에 써본 것", "결과 예시가 있는 것", "사용 방법이 명확한 것",
             "초보자가 따라할 수 있는 것", "특정 툴/버전/환경 조건이 적혀 있는 것",
             "개인정보/고객정보/회사기밀이 없는 것", "저작권 문제가 없는 것",
             "구매자가 바로 써볼 수 있는 것"]
FRAMES = [{"name": "list", "width": 390, "height": 844}, {"name": "detail", "width": 390, "height": 844}]


def passing_state():
    return {
        "refs": 5,
        "bullets": 3,
        "s2_headings": ["역할별 접근", "허용 상태값", "범위 밖 항목"],
        "s2_extra": "",
        "approval": "승인자: 김하이\n날짜: 2026-10-11\n승인\n",
        "s2": {
            "sale_requested_roles": ["seller"],
            "asset_default_visibility": "비공개",
            "approve_button_enabled_when": "체크리스트 8/8 완료",
            "review_checklist": list(CHECKLIST),
            "review_flow": [["draft", "pending", "approved"]],
            "statuses": {"submission": ["draft", "submitted"], "visibility": ["private", "member_only", "sale_requested"],
                         "review": ["draft", "pending", "revision_requested", "approved", "rejected"]},
            "paid_content_exposure": {"free": "preview", "guest": "none"},
        },
        "s3": {"frames": copy.deepcopy(FRAMES), "horizontal_scroll_360": False, "side_padding": 16},
        "comp": {"shadows": [], "interactive": [{"name": "cta", "radius": 9999, "height": 44}],
                 "inputs": [{"name": "title", "rest_border": False}]},
        "scr": {"accent_uses": [{"page": "home", "kind": "commercial"}], "uppercase_text": [],
                "gradients_chrome": [], "colored_bands": [], "extra_accent_hues": [], "portraits": [],
                "status_badges": [{"label": "검수 대기", "color_only": False}],
                "colors": ["#141414"], "spacings": [16, 24]},
        "tok": {"colors": {"primary": "#141414", "accent": "#0066ff"},
                "radius": {"full": 9999, "md": 24, "app-icon": "30%"},
                "font": {"family": "Pretendard"},
                "typography": {"heading-1": {"size": 28, "weight": 700, "lineHeight": 1.3},
                               "body": {"size": 15, "weight": 400, "lineHeight": 1.5}},
                "letterSpacing": 0, "spacing": {"md": 16}},
    }


def block(d):
    return "```json\n" + json.dumps(d, ensure_ascii=False, indent=2) + "\n```\n"


def write_run(root, S):
    run = Path(root) / "runs" / SLUG
    run.mkdir(parents=True, exist_ok=True)
    links = "\n".join("- https://uibowl.io/view/%d" % i for i in range(S["refs"]))
    (run / "s1-references.md").write_text("# 레퍼런스\n" + links + "\n", encoding="utf-8")
    bullets = "\n".join("- 반영 %d" % i for i in range(S["bullets"]))
    (run / "s1-analysis.md").write_text("# 분석\n## 반영할 부분\n" + bullets + "\n", encoding="utf-8")
    heads = "\n".join("## " + h + "\n내용\n" for h in S["s2_headings"])
    # 범위 밖 섹션에 키워드가 있어도 통과해야 한다
    heads = heads.replace("## 범위 밖 항목\n내용", "## 범위 밖 항목\n허들링 픽, 정산 내역은 만들지 않는다")
    # 위반 문구는 '범위 밖 항목' 섹션 아래로 들어가면 안 되므로 제목들보다 앞에 둔다
    (run / "s2-spec.md").write_text("# 설계\n" + S["s2_extra"] + "\n" + heads + "\n" + block(S["s2"]), encoding="utf-8")
    (run / "s3-keyscreens.md").write_text("# 키스크린\n" + block(S["s3"]), encoding="utf-8")
    if S["approval"] is not None:
        (run / "s3-approval.md").write_text(S["approval"], encoding="utf-8")
    (run / "s4-components.md").write_text("# 컴포넌트\n" + block(S["comp"]), encoding="utf-8")
    scr = dict(S["scr"])
    (run / "s4-screens.md").write_text("# 화면\n" + block(scr), encoding="utf-8")
    (run / "s4-tokens.json").write_text(json.dumps(S["tok"]), encoding="utf-8")
    return run


def make_root():
    root = Path(tempfile.mkdtemp())
    (root / "harness").mkdir()
    for name in ("gates.md", "default-design.md", "default-content.md"):
        shutil.copy(HARNESS / name, root / "harness" / name)
    return root


def mutate(gid):
    S = passing_state()
    if gid == "D1": S["tok"]["colors"]["bad"] = "#ff0000"
    elif gid == "D2": S["scr"]["accent_uses"].append({"page": "home", "kind": "cta"})
    elif gid == "D3": S["comp"]["shadows"] = ["card"]
    elif gid == "D4": S["comp"]["interactive"][0]["radius"] = 8
    elif gid == "D5": S["tok"]["font"]["family"] = "Arial"
    elif gid == "D6": S["tok"]["letterSpacing"] = 0.5
    elif gid == "D7": S["comp"]["inputs"][0]["rest_border"] = True
    elif gid == "D8": S["scr"]["gradients_chrome"] = ["hero"]
    elif gid == "D9": S["scr"]["portraits"] = [{"name": "curator", "grayscale": False}]
    elif gid == "D10": S["s3"]["horizontal_scroll_360"] = True
    elif gid == "D11": S["comp"]["interactive"][0]["height"] = 40
    elif gid == "D12": S["tok"]["spacing"]["md"] = 15
    elif gid == "D13": S["scr"]["status_badges"][0]["color_only"] = True
    elif gid == "C1": S["s2"]["sale_requested_roles"] = ["seller", "paid"]
    elif gid == "C2": S["s2"]["asset_default_visibility"] = "멤버 공개"
    elif gid == "C3": S["s2"]["approve_button_enabled_when"] = "검수 요청 후"
    elif gid == "C4": S["s2_extra"] = "\n문의: hello@example.com\n"
    elif gid == "C5": S["s2"]["review_flow"] = [["draft", "approved"]]
    elif gid == "C6": S["s2"]["statuses"]["review"].append("suspended")
    elif gid == "C7": S["s2_extra"] = "\n허들링 픽 목록 화면을 둔다\n"
    elif gid == "C8": S["s2"]["paid_content_exposure"]["free"] = "full"
    elif gid == "P1": S["refs"] = 3
    elif gid == "P2": S["s2_headings"] = ["역할별 접근", "허용 상태값"]
    elif gid == "P3": S["s3"]["frames"] = S["s3"]["frames"][:1]
    elif gid == "P4": S["approval"] = None
    elif gid == "P5": S["tok"]["radius"]["bad"] = 8
    else: raise KeyError(gid)
    return S


STAGE_OF = {"P1": "S1", "P2": "S2", "P3": "S3", "P4": "S3", "P5": "S4"}
ALL_IDS = ["D%d" % i for i in range(1, 14)] + ["C%d" % i for i in range(1, 9)] + ["P%d" % i for i in range(1, 6)]


class VerdictTest(unittest.TestCase):
    def setUp(self):
        self.root = make_root()
        self.addCleanup(shutil.rmtree, self.root, True)

    def run_stage(self, S, stage, root=None):
        write_run(root or self.root, S)
        return verdict.judge(root or self.root, SLUG, stage)

    def test_every_gate_has_a_check(self):
        gates = verdict.load_gates(HARNESS / "gates.md")
        self.assertEqual(sorted(gates), sorted(ALL_IDS))
        self.assertEqual(set(gates), set(verdict.CHECKS))

    def test_pass_sample_has_zero_violations_at_every_stage(self):
        write_run(self.root, passing_state())
        for stage in verdict.STAGES:
            report, code = verdict.judge(self.root, SLUG, stage)
            self.assertEqual(report["violations"], [], stage)
            self.assertEqual(code, 0, stage)
        report, _ = verdict.judge(self.root, SLUG, "S5")
        self.assertEqual(len(report["checked"]), 21)  # D1~D13 + C1~C8

    def test_each_violation_sample_is_detected_by_its_own_id(self):
        for gid in ALL_IDS:
            with self.subTest(gate=gid):
                root = make_root()
                self.addCleanup(shutil.rmtree, root, True)
                stage = STAGE_OF.get(gid, "S5")
                report, code = self.run_stage(mutate(gid), stage, root)
                self.assertEqual(code, 1)
                self.assertIn(gid, {v["id"] for v in report["violations"]})
                # 다른 ID는 걸리지 않아야 한다 (한 군데만 고쳤으므로)
                self.assertEqual({v["id"] for v in report["violations"]}, {gid})

    def test_missing_attribute_is_a_violation_not_a_pass(self):
        S = passing_state()
        del S["comp"]["shadows"]
        report, code = self.run_stage(S, "S5")
        self.assertEqual(code, 1)
        self.assertIn("D3", {v["id"] for v in report["violations"]})

    def test_return_targets(self):
        report, _ = self.run_stage(mutate("D3"), "S5")
        self.assertEqual(report["return_to"], "S4")
        root = make_root()
        self.addCleanup(shutil.rmtree, root, True)
        report, _ = self.run_stage(mutate("C2"), "S5", root)
        self.assertEqual(report["return_to"], "S2")

    def test_exit_code_2_after_three_returns(self):
        run = write_run(self.root, mutate("D3"))
        (run / "state.json").write_text(json.dumps({"returns": {"S4": 3}}), encoding="utf-8")
        _, code = verdict.judge(self.root, SLUG, "S5")
        self.assertEqual(code, 2)
        (run / "state.json").write_text(json.dumps({"returns": {"S4": 2}}), encoding="utf-8")
        _, code = verdict.judge(self.root, SLUG, "S5")
        self.assertEqual(code, 1)

    def test_versioned_file_counts_as_return_and_latest_wins(self):
        S = mutate("D3")
        run = write_run(self.root, S)
        fixed = passing_state()
        (run / "s4-components-v2.md").write_text("# 컴포넌트 v2\n" + block(fixed["comp"]), encoding="utf-8")
        report, code = verdict.judge(self.root, SLUG, "S5")
        self.assertEqual(code, 0, report["violations"])  # v2 가 최신이다
        for n in (3, 4):
            (run / ("s4-components-v%d.md" % n)).write_text("# 컴포넌트\n" + block(S["comp"]), encoding="utf-8")
        _, code = verdict.judge(self.root, SLUG, "S5")
        self.assertEqual(code, 2)  # v4 = 3회 되돌림, 위반이 남아 있으면 멈춤

    def test_missing_run_dir(self):
        report, code = verdict.judge(self.root, "no-such-slug", "S5")
        self.assertEqual(code, 1)
        self.assertEqual(report["violations"][0]["id"], "INPUT")

    def test_main_writes_report(self):
        write_run(self.root, mutate("D3"))
        code = verdict.main([SLUG, "--stage", "S5", "--root", str(self.root)])
        self.assertEqual(code, 1)
        data = json.loads((self.root / "runs" / SLUG / "s5-report.json").read_text(encoding="utf-8"))
        self.assertFalse(data["passed"])


if __name__ == "__main__":
    unittest.main()
