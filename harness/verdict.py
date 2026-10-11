#!/usr/bin/env python3
"""판정 스크립트. 명세: harness/verdict-spec.md

사용법: python3 harness/verdict.py <slug> --stage S1|S2|S3|S4|S5 [--root <프로젝트 루트>]

규칙(D·C·P)의 원본은 harness/gates.md, 값은 harness/default-*.md 이다.
이 스크립트는 그 표를 읽고, ID별 검사 함수만 가진다. 쓰는 파일은 s5-report.json 하나뿐이다.
종료 코드: 0 = 통과, 1 = 위반 있음, 2 = 되돌림 상한 초과(멈춤)
"""
import argparse
import json
import re
import sys
from pathlib import Path

STAGES = ["S1", "S2", "S3", "S4", "S5"]
# gates.md 의 "걸리는 단계"는 docs/story-work.md 문장 번호다. 단계와의 대응은 pipeline.md 기준.
STAGE_SENTENCES = {
    "S1": {"1", "2"},
    "S2": {"3"},
    "S3": {"4", "5"},
    "S4": {"6-a", "6-b", "6-c"},
    "S5": {"7"},
}
RETURN_LIMIT = 3  # pipeline.md: 같은 단계로 3회까지, 4회째에 멈춘다
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"\b0\d{1,2}-?\d{3,4}-?\d{4}\b")
UIBOWL_RE = re.compile(r"https?://[^\s)\]>]*uibowl[^\s)\]>]*")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
JSON_BLOCK_RE = re.compile(r"```json\s*\n(.*?)\n```", re.S)


class Missing(Exception):
    """판정에 필요한 속성이 기록되지 않았다."""


# ---------------------------------------------------------------- 규칙·값 읽기

def read(path):
    return Path(path).read_text(encoding="utf-8")


def sections(text):
    out, name, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if name is not None:
                out[name] = "\n".join(buf)
            name, buf = line[3:].strip(), []
        elif name is not None:
            buf.append(line)
    if name is not None:
        out[name] = "\n".join(buf)
    return out


def section(secs, prefix):
    for k, v in secs.items():
        if k.startswith(prefix):
            return v
    raise SystemExit("harness 파일에서 섹션을 찾지 못했다: " + prefix)


def table_cells(line):
    parts = [p.strip() for p in line.strip().split("|")]
    return parts[1:-1]


def load_gates(path):
    """gates.md -> {id: {"kind": D|C|P, "stages": set}}"""
    gates = {}
    for line in read(path).splitlines():
        if not line.startswith("|"):
            continue
        cells = table_cells(line)
        if not cells:
            continue
        gid = cells[0].replace("★", "").strip()
        if re.fullmatch(r"[DC]\d+", gid) and len(cells) == 4:
            nums = {s.strip() for s in cells[3].split(",")}
            gates[gid] = {"kind": gid[0], "sentences": nums}
        elif re.fullmatch(r"P\d+", gid) and len(cells) == 3:
            m = re.match(r"S\d", cells[2])
            gates[gid] = {"kind": "P", "stage": m.group(0) if m else None}
    return gates


def load_design(path):
    secs = sections(read(path))
    colors = section(secs, "Colors")
    palette = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}", colors)}
    palette |= {re.sub(r"\s+", "", r) for r in re.findall(r"rgba\([^)]*\)", colors)}
    typo = section(secs, "Typography")
    rows = set()
    for line in typo.splitlines():
        m = re.match(r"^\|\s*([a-z0-9-]+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|", line)
        if m:
            rows.add((int(m.group(2)), int(m.group(3)), float(m.group(4))))
    shape = section(secs, "Shape")
    radius = {int(x) for x in re.findall(r"(\d+)px", shape)}
    radius_pct = {x + "%" for x in re.findall(r"(\d+)%", shape)}
    layout = section(secs, "Layout")
    fw, fh = re.search(r"(\d+)×(\d+)", layout).groups()
    return {
        "palette": palette,
        "typography": rows,
        "font": "Pretendard",
        "radius": radius,
        "radius_pct": radius_pct,
        "frame": (int(fw), int(fh)),
        "padding": int(re.search(r"좌우 패딩 (\d+)", layout).group(1)),
        "touch_min": int(re.search(r"터치 타깃 최소 (\d+)px", layout).group(1)),
        "accent_max": int(re.search(r"페이지당 1~(\d+)개", colors).group(1)),
    }


def load_content(path):
    secs = sections(read(path))
    allowed = {}
    for line in section(secs, "허용 상태값").splitlines():
        cells = table_cells(line) if line.startswith("|") else []
        if len(cells) >= 2 and re.match(r"(Submission|Asset)\.", cells[0]):
            allowed[cells[0]] = set(re.findall(r"`([^`]+)`", cells[1]))
    out_of_scope = section(secs, "범위 밖")
    kw_part = out_of_scope.split("검출 키워드", 1)[-1]
    keywords = [m.strip() for m in re.findall(r"^- (.+)$", kw_part, re.M)]
    return {
        "submission": allowed["Submission.status"],
        "visibility": allowed["Asset.visibility"],
        "review": allowed["Asset.review_status"],
        "keywords": keywords,
    }


# ---------------------------------------------------------------- 산출물 읽기

def latest(run_dir, base, ext):
    """base.ext 또는 base-vN.ext 중 가장 최신 파일. 없으면 None."""
    best, best_n = None, -1
    for p in run_dir.glob(base + "*" + ext):
        m = re.fullmatch(re.escape(base) + r"(?:-v(\d+))?" + re.escape(ext), p.name)
        if m:
            n = int(m.group(1)) if m.group(1) else 1
            if n > best_n:
                best, best_n = p, n
    return best


def merge(dst, src):
    for k, v in src.items():
        if isinstance(v, list) and isinstance(dst.get(k), list):
            dst[k].extend(v)
        elif isinstance(v, dict) and isinstance(dst.get(k), dict):
            dst[k].update(v)
        else:
            dst[k] = v


def strip_out_of_scope(text):
    """'범위 밖' 이 들어간 제목 아래 본문은 키워드 검출에서 제외한다."""
    out, skip = [], False
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s", line):
            skip = "범위 밖" in line
        if not skip:
            out.append(line)
    return "\n".join(out)


def load_run(run_dir):
    ctx = {"attrs": {}, "tokens": None, "text": "", "files": {}, "parse_errors": []}
    for base in ("s2-spec", "s3-keyscreens", "s4-components", "s4-screens"):
        p = latest(run_dir, base, ".md")
        if not p:
            continue
        txt = read(p)
        ctx["files"][base] = p.name
        ctx["text"] += "\n" + txt
        m = JSON_BLOCK_RE.search(txt)
        if m:
            try:
                merge(ctx["attrs"], json.loads(m.group(1)))
            except ValueError as e:
                ctx["parse_errors"].append((p.name, str(e)))
    p = latest(run_dir, "s4-tokens", ".json")
    if p:
        ctx["files"]["s4-tokens"] = p.name
        try:
            ctx["tokens"] = json.loads(read(p))
        except ValueError as e:
            ctx["parse_errors"].append((p.name, str(e)))
    return ctx


# ---------------------------------------------------------------- 검사 함수
# 각 함수는 [(file, location, detail), ...] 를 돌려준다. 빈 리스트 = 통과.

def need(ctx, key):
    if key not in ctx["attrs"]:
        raise Missing("속성 미기록: " + key)
    return ctx["attrs"][key]


def need_tokens(ctx):
    if ctx["tokens"] is None:
        raise Missing("s4-tokens.json 없음")
    return ctx["tokens"]


def norm_color(v):
    return re.sub(r"\s+", "", str(v)).lower()


def tok_colors(ctx, D):
    t = need_tokens(ctx)
    return [("s4-tokens.json", "colors." + k, "허용 색상 밖: " + str(v))
            for k, v in t.get("colors", {}).items() if norm_color(v) not in D["palette"]]


def tok_radius(ctx, D):
    t = need_tokens(ctx)
    bad = []
    for k, v in t.get("radius", {}).items():
        ok = (isinstance(v, (int, float)) and int(v) in D["radius"]) or v in D["radius_pct"]
        if not ok:
            bad.append(("s4-tokens.json", "radius." + k, "허용 반지름 밖: " + str(v)))
    return bad


def tok_font(ctx, D):
    t = need_tokens(ctx)
    fam = str(t.get("font", {}).get("family", ""))
    bad = []
    if not fam.startswith(D["font"]):
        bad.append(("s4-tokens.json", "font.family", "Pretendard 아님: " + fam))
    return bad


def d1(ctx, D, K):
    bad = tok_colors(ctx, D)
    for v in ctx["attrs"].get("colors", []):
        if norm_color(v) not in D["palette"]:
            bad.append(("s4-screens.md", "colors", "허용 색상 밖: " + str(v)))
    return bad


def d2(ctx, D, K):
    uses = need(ctx, "accent_uses")
    bad = [("s4-screens.md", u.get("page", "?"), "accent가 CTA에 쓰임")
           for u in uses if u.get("kind") == "cta"]
    pages = {}
    for u in uses:
        pages[u.get("page", "?")] = pages.get(u.get("page", "?"), 0) + 1
    bad += [("s4-screens.md", p, "accent %d개 (최대 %d)" % (n, D["accent_max"]))
            for p, n in pages.items() if n > D["accent_max"]]
    return bad


def d3(ctx, D, K):
    return [("s4-components.md", str(s), "box-shadow 사용")
            for s in need(ctx, "shadows") if s != "segmented-control-active"]


def d4(ctx, D, K):
    return [("s4-components.md", i.get("name", "?"), "반지름 %s (9999 아님)" % i.get("radius"))
            for i in need(ctx, "interactive") if i.get("radius") != 9999]


def d5(ctx, D, K):
    bad = tok_font(ctx, D)
    t = need_tokens(ctx)
    for name, v in t.get("typography", {}).items():
        key = (v.get("size"), v.get("weight"), float(v.get("lineHeight", 0)))
        if key not in D["typography"]:
            bad.append(("s4-tokens.json", "typography." + name, "타이포 표에 없는 조합: %s" % (key,)))
        if re.match(r"(heading|display)", name) and v.get("weight") != 700:
            bad.append(("s4-tokens.json", "typography." + name, "제목 굵기 700 아님"))
    return bad


def d6(ctx, D, K):
    t = need_tokens(ctx)
    bad = []
    if t.get("letterSpacing", None) != 0:
        bad.append(("s4-tokens.json", "letterSpacing", "0이 아니거나 미기록: %s" % t.get("letterSpacing")))
    bad += [("s4-screens.md", str(x), "대문자 변환") for x in need(ctx, "uppercase_text")]
    return bad


def d7(ctx, D, K):
    return [("s4-components.md", i.get("name", "?"), "평상시 테두리 있음")
            for i in need(ctx, "inputs") if i.get("rest_border")]


def d8(ctx, D, K):
    bad = []
    for key, msg in (("gradients_chrome", "UI 크롬 그라디언트"),
                     ("colored_bands", "색칠된 섹션 띠"),
                     ("extra_accent_hues", "추가 강조 색상")):
        bad += [("s4-screens.md", str(x), msg) for x in need(ctx, key)]
    return bad


def d9(ctx, D, K):
    return [("s4-screens.md", p.get("name", "?"), "포트레이트가 흑백 아님")
            for p in need(ctx, "portraits") if not p.get("grayscale")]


def d10(ctx, D, K):
    bad = []
    fw, fh = D["frame"]
    frames = need(ctx, "frames")
    for f in frames:
        if (f.get("width"), f.get("height")) != (fw, fh):
            bad.append(("frames", f.get("name", "?"), "프레임 %sx%s (%dx%d 아님)" % (f.get("width"), f.get("height"), fw, fh)))
    if need(ctx, "horizontal_scroll_360"):
        bad.append(("attrs", "horizontal_scroll_360", "360px에서 가로 스크롤 발생"))
    if need(ctx, "side_padding") != D["padding"]:
        bad.append(("attrs", "side_padding", "좌우 패딩이 %d 아님" % D["padding"]))
    return bad


def d11(ctx, D, K):
    return [("s4-components.md", i.get("name", "?"), "높이 %s < %d" % (i.get("height"), D["touch_min"]))
            for i in need(ctx, "interactive")
            if not isinstance(i.get("height"), (int, float)) or i["height"] < D["touch_min"]]


def d12(ctx, D, K):
    t = need_tokens(ctx)
    vals = list(t.get("spacing", {}).items()) + [("spacings", v) for v in ctx["attrs"].get("spacings", [])]
    return [("spacing", str(k), "4의 배수 아님: %s" % v) for k, v in vals
            if not isinstance(v, (int, float)) or v % 4 != 0]


def d13(ctx, D, K):
    return [("s4-screens.md", b.get("label", "?"), "색으로만 구분")
            for b in need(ctx, "status_badges") if b.get("color_only") or not b.get("label")]


def c1(ctx, D, K):
    roles = set(need(ctx, "sale_requested_roles"))
    return [] if roles == {"seller"} else [("attrs", "sale_requested_roles", "seller 외 역할 포함 또는 비어 있음: %s" % sorted(roles))]


def c2(ctx, D, K):
    v = need(ctx, "asset_default_visibility")
    return [] if v in ("비공개", "private") else [("attrs", "asset_default_visibility", "기본값이 비공개 아님: %s" % v)]


def c3(ctx, D, K):
    v = str(need(ctx, "approve_button_enabled_when"))
    return [] if "8/8" in v else [("attrs", "approve_button_enabled_when", "체크리스트 8/8 조건 없음")]


def c4(ctx, D, K):
    bad = []
    for rx, label in ((EMAIL_RE, "이메일"), (PHONE_RE, "전화번호")):
        for m in rx.findall(ctx["text"]):
            bad.append(("text", m, label + " 패턴 검출"))
    items = need(ctx, "review_checklist")
    if len(items) != 8:
        bad.append(("attrs", "review_checklist", "체크리스트가 8개 아님: %d" % len(items)))
    else:
        if "개인정보" not in items[5]:
            bad.append(("attrs", "review_checklist[6]", "6번 문항에 개인정보 없음"))
        if "저작권" not in items[6]:
            bad.append(("attrs", "review_checklist[7]", "7번 문항에 저작권 없음"))
    return bad


def c5(ctx, D, K):
    bad = []
    for flow in need(ctx, "review_flow"):
        if "approved" in flow:
            i = flow.index("approved")
            if "pending" not in flow[:i]:
                bad.append(("attrs", "review_flow", "pending 없이 approved: %s" % " > ".join(flow)))
    return bad


def c6(ctx, D, K):
    st = need(ctx, "statuses")
    bad = []
    for key in ("submission", "visibility", "review"):
        for v in st.get(key, []):
            if v not in K[key]:
                bad.append(("attrs", "statuses." + key, "허용되지 않은 값: " + str(v)))
    return bad


def c7(ctx, D, K):
    text = strip_out_of_scope(ctx["text"])
    return [("text", kw, "범위 밖 키워드 검출") for kw in K["keywords"] if kw in text]


def c8(ctx, D, K):
    exp = need(ctx, "paid_content_exposure")
    return [("attrs", "paid_content_exposure." + r, "본문 전체 노출: %s" % exp.get(r))
            for r in ("free", "guest") if exp.get(r) not in ("preview", "none")]


def p1(ctx, D, K):
    run = ctx["run_dir"]
    ref, ana = latest(run, "s1-references", ".md"), latest(run, "s1-analysis", ".md")
    if not ref or not ana:
        raise Missing("s1-references.md 또는 s1-analysis.md 없음")
    bad = []
    n = len(set(UIBOWL_RE.findall(read(ref))))
    if n < 5:
        bad.append((ref.name, "uibowl 링크", "%d개 (5개 이상 필요)" % n))
    count = 0
    for k, body in re.findall(r"^#+\s*(.*)\n((?:(?!^#).*\n?)*)", read(ana), re.M):
        if "반영할 부분" in k:
            count += len(re.findall(r"^\s*(?:[-*]|\d+\.)\s+\S", body, re.M))
    if count < 3:
        bad.append((ana.name, "반영할 부분", "%d개 (3개 이상 필요)" % count))
    return bad


def p2(ctx, D, K):
    p = latest(ctx["run_dir"], "s2-spec", ".md")
    if not p:
        raise Missing("s2-spec.md 없음")
    heads = " ".join(re.findall(r"^#+\s*(.*)$", read(p), re.M))
    return [(p.name, h, "필수 섹션 없음") for h in ("역할별 접근", "허용 상태값", "범위 밖 항목") if h not in heads]


def p3(ctx, D, K):
    frames = need(ctx, "frames")
    bad = []
    if not 2 <= len(frames) <= 3:
        bad.append(("s3-keyscreens.md", "frames", "키스크린 %d개 (2~3개 필요)" % len(frames)))
    fw, fh = D["frame"]
    bad += [("s3-keyscreens.md", f.get("name", "?"), "프레임 크기 %sx%s" % (f.get("width"), f.get("height")))
            for f in frames if (f.get("width"), f.get("height")) != (fw, fh)]
    return bad


def p4(ctx, D, K):
    p = ctx["run_dir"] / "s3-approval.md"
    if not p.exists():
        return [("s3-approval.md", "-", "승인 파일 없음")]
    t = read(p)
    bad = []
    if not re.search(r"승인자\s*[:：]\s*\S+", t):
        bad.append((p.name, "승인자", "승인자 이름 없음"))
    if not DATE_RE.search(t):
        bad.append((p.name, "날짜", "날짜(YYYY-MM-DD) 없음"))
    if "승인" not in t.replace("승인자", ""):
        bad.append((p.name, "승인", "'승인' 문자열 없음"))
    return bad


def p5(ctx, D, K):
    return tok_colors(ctx, D) + tok_radius(ctx, D) + tok_font(ctx, D)


CHECKS = {
    "D1": d1, "D2": d2, "D3": d3, "D4": d4, "D5": d5, "D6": d6, "D7": d7,
    "D8": d8, "D9": d9, "D10": d10, "D11": d11, "D12": d12, "D13": d13,
    "C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5": c5, "C6": c6, "C7": c7, "C8": c8,
    "P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5,
}


# ---------------------------------------------------------------- 실행

def selected(gates, stage):
    ids = []
    for gid, g in gates.items():
        if g["kind"] == "P":
            if g["stage"] == stage:
                ids.append(gid)
        elif g["sentences"] & STAGE_SENTENCES[stage]:
            ids.append(gid)
    return sorted(ids, key=lambda x: (x[0], int(x[1:])))


def return_target(violation_ids, stage):
    """pipeline.md: D 위반 -> S4, C 위반 -> S2, P 위반 -> 그 단계. 현재 단계보다 앞으로만 간다."""
    cands = []
    for vid in violation_ids:
        if vid.startswith("C"):
            cands.append("S2")
        elif vid.startswith("D"):
            cands.append("S4")
        else:
            cands.append(stage)
    if not cands:
        return None
    first = min(cands, key=STAGES.index)
    return first if STAGES.index(first) <= STAGES.index(stage) else stage


def returns_count(run_dir, stage):
    """state.json 의 기록과 -vN 파일 수 중 큰 값."""
    n = 0
    sj = run_dir / "state.json"
    if sj.exists():
        try:
            n = int(json.loads(read(sj)).get("returns", {}).get(stage, 0))
        except (ValueError, AttributeError):
            pass
    prefix = "s" + stage[1]
    for p in run_dir.glob(prefix + "*-v*"):
        m = re.search(r"-v(\d+)\.", p.name)
        if m:
            n = max(n, int(m.group(1)) - 1)
    return n


def judge(root, slug, stage):
    root = Path(root)
    run_dir = root / "runs" / slug
    harness = root / "harness"
    violations, checked = [], []
    if not run_dir.is_dir():
        report = {"slug": slug, "stage": stage, "checked": [], "passed": False, "return_to": None,
                  "violations": [{"id": "INPUT", "file": str(run_dir), "location": "-", "detail": "runs/<slug> 폴더 없음"}]}
        return report, 1
    gates = load_gates(harness / "gates.md")
    D = load_design(harness / "default-design.md")
    K = load_content(harness / "default-content.md")
    ctx = load_run(run_dir)
    ctx["run_dir"] = run_dir
    for fname, err in ctx["parse_errors"]:
        violations.append({"id": "PARSE", "file": fname, "location": "-", "detail": "JSON 해석 실패: " + err})
    for gid in selected(gates, stage):
        checked.append(gid)
        fn = CHECKS.get(gid)
        if fn is None:
            violations.append({"id": gid, "file": "-", "location": "-", "detail": "검사 함수 없음 (판정 불가)"})
            continue
        try:
            for f, loc, detail in fn(ctx, D, K):
                violations.append({"id": gid, "file": f, "location": loc, "detail": detail})
        except Missing as e:
            violations.append({"id": gid, "file": "-", "location": "-", "detail": str(e)})
    ids = [v["id"] for v in violations if v["id"] not in ("PARSE", "INPUT")]
    target = return_target(ids, stage) if ids else None
    if violations and target is None:
        target = stage
    report = {"slug": slug, "stage": stage, "checked": checked,
              "passed": not violations, "return_to": target, "violations": violations}
    if not violations:
        return report, 0
    if returns_count(run_dir, target) >= RETURN_LIMIT:
        return report, 2
    return report, 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="허들링 하네스 판정 스크립트")
    ap.add_argument("slug")
    ap.add_argument("--stage", required=True, choices=STAGES)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args(argv)
    report, code = judge(args.root, args.slug, args.stage)
    run_dir = Path(args.root) / "runs" / args.slug
    if run_dir.is_dir():
        (run_dir / "s5-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    label = {0: "통과", 1: "위반 있음", 2: "되돌림 상한 초과 - 멈추고 사람에게 알린다"}[code]
    print("[%s %s] %s (검사 %d개, 위반 %d건)" % (args.slug, args.stage, label, len(report["checked"]), len(report["violations"])))
    for v in report["violations"]:
        print("  - %s %s %s: %s" % (v["id"], v["file"], v["location"], v["detail"]))
    if report["return_to"]:
        print("  돌아갈 단계: " + report["return_to"])
    return code


if __name__ == "__main__":
    sys.exit(main())
