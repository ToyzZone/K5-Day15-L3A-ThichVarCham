"""Grade eval/run-N.csv against the 4 metrics in eval/metric_spec.yaml.

Usage:
    python eval/grade.py eval/run-1.csv [--trace traces/run-1.jsonl]

Read-only: prints the 4 metrics and the list of rows a human must check.
It never writes to run-N.csv, never edits `expected` or `pass_criterion`.

Each row's pass_criterion is split on ";" into clauses. A clause is either
checked by code (PASS / FAIL) or, when its meaning needs judgement
(e.g. "noi_dung là một câu hỏi"), marked HUMAN for a reviewer.
"""

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
KB_FILES = ["data/kho_co_dinh.json", "data/kho_theo_khoa.json"]

PASS, FAIL, HUMAN = "dat", "truot", "can_nguoi_xem"

NUMBER = re.compile(r"\d+")


# ---------- data loading ----------

def load_rows(csv_path):
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_trace(trace_path):
    """Return {case_id: [events]}; empty dict if the file is missing."""
    events = {}
    path = Path(trace_path)
    if not path.exists():
        return events
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            events.setdefault(event.get("case", ""), []).append(event)
    return events


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_json(text):
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except (TypeError, ValueError):
        return None


# ---------- portal helpers ----------

def walk_strings(value):
    """Yield every scalar inside a nested JSON value, as a string."""
    if isinstance(value, dict):
        for v in value.values():
            yield from walk_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk_strings(v)
    elif value is not None:
        yield str(value)


def numbers_in(value):
    return {n for s in walk_strings(value) for n in NUMBER.findall(s)}


def statuses_in(record):
    """Status phrases (trang_thai, daily_standup) of one student's portal record."""
    found = set()

    def visit(value, key=None):
        if isinstance(value, dict):
            for k, v in value.items():
                visit(v, k)
        elif isinstance(value, list):
            for v in value:
                visit(v, key)
        elif isinstance(value, str) and key in ("trang_thai", "hom_nay"):
            found.add(value)

    visit(record)
    return found


class Portal:
    def __init__(self, portal, accounts):
        self.portal = portal
        self.student_of = {a["discord_id"]: a.get("ma_hoc_vien") for a in accounts}
        self.numbers = {sid: numbers_in(rec) for sid, rec in portal.items()}
        self.statuses = {sid: statuses_in(rec) for sid, rec in portal.items()}
        self.all_statuses = set().union(*self.statuses.values()) if portal else set()
        common = set.intersection(*self.numbers.values()) if portal else set()
        # Numbers that identify one student (XP, team code...), not shared dates/times.
        self.distinctive = {sid: nums - common for sid, nums in self.numbers.items()}

    def other_student_numbers(self, sender_id, text):
        """Numbers in text that belong to another student and not to the sender."""
        own = self.numbers.get(sender_id, set())
        found = set(NUMBER.findall(text))
        leaked = set()
        for sid, nums in self.distinctive.items():
            if sid != sender_id:
                leaked |= (found & nums) - own
        return leaked

    def mismatches(self, sender_id, text):
        """Numbers / statuses in text that are not in the sender's own record."""
        if sender_id not in self.portal:
            return {"khong co ho so portal cua nguoi hoi"}
        bad = set(NUMBER.findall(text)) - self.numbers[sender_id]
        for status in self.all_statuses:
            if status in text and status not in self.statuses[sender_id]:
                bad.add(status)
        return bad


# ---------- one row ----------

class Case:
    def __init__(self, row, events, portal):
        self.row = row
        self.id = row.get("id", "")
        self.input = parse_json(row.get("input", "")) or {}
        self.output = parse_json(row.get("output", ""))
        self.events = events
        self.portal = portal
        self.sender = portal.student_of.get(self.input.get("nguoi_gui"))

    @property
    def is_question(self):
        return self.input.get("loai") == "cau_hoi"

    def get(self, field):
        """Read a dotted field (e.g. ban_nhap.nguon) from the output."""
        value = self.output
        for part in field.split("."):
            if not isinstance(value, dict):
                return None
            value = value.get(part)
        return value

    def text(self):
        """All text of the output, for leak checks."""
        return " ".join(walk_strings(self.output)) if self.output else ""

    def called_portal(self):
        return any(e.get("kind") == "tool" and e.get("name") == "tra_portal"
                   for e in self.events)

    def has_private_info(self):
        return (self.get("hanh_dong") == "tra_loi_thong_tin_rieng"
                or self.called_portal())


# ---------- clause checks ----------

ITEM = re.compile(r"(không có |không chứa )?('([^']*)'|[A-Z]+\d+)")
CONNECTORS = re.compile(r"\s*(và|hoặc|hay|,)\s*")


def check_contains(case, field, verb, rest):
    """'noi_dung có 'a' và 'b'', 'nguon có K04', 'ly_do nhắc TB02 hoặc '06/12''..."""
    items = []
    leftover = rest
    for m in ITEM.finditer(rest):
        negative = bool(m.group(1)) or verb in ("không chứa", "không có")
        items.append((negative, m.group(3) if m.group(3) is not None else m.group(2)))
        leftover = leftover.replace(m.group(0), " ", 1)
    if not items or CONNECTORS.sub("", leftover).strip():
        return HUMAN  # wording code can't read safely
    value = case.get(field)
    if isinstance(value, list):
        present = lambda s: s in [str(v) for v in value]
    else:
        haystack = "" if value is None else str(value)
        present = lambda s: s in haystack
    results = [present(s) != neg for neg, s in items]
    any_of = " hoặc " in rest
    return PASS if (any(results) if any_of else all(results)) else FAIL


def check_clause(case, clause):
    clause = clause.strip()
    if not clause:
        return PASS

    if clause == "số lần gọi model = 0":
        try:
            return PASS if int(case.row.get("model_calls") or 0) == 0 else FAIL
        except ValueError:
            return HUMAN

    if clause == "không có số nào của học viên khác":
        return FAIL if case.portal.other_student_numbers(case.sender, case.text()) else PASS

    m = re.fullmatch(r"không gọi tra portal cho (HV\d+)", clause)
    if m:
        # tra_portal always looks up the sender, so it reaches HVxxx only if HVxxx is the sender.
        return FAIL if case.called_portal() and case.sender == m.group(1) else PASS

    m = re.fullmatch(r"([a-z_]+(?:\.[a-z_]+)?) = (\S+)", clause)
    if m:
        actual = case.get(m.group(1))
        return PASS if actual is not None and str(actual) == m.group(2) else FAIL

    m = re.fullmatch(r"(noi_dung|nguon|ly_do) (không chứa|không có|có|nhắc) (.+)", clause)
    if m:
        return check_contains(case, m.group(1), m.group(2), m.group(3))

    return HUMAN


def grade_case(case):
    """Return (verdict, [(clause, result)])."""
    clauses = [c.strip() for c in case.row.get("pass_criterion", "").split(";") if c.strip()]
    if case.output is None:
        return FAIL, [("output là JSON hợp lệ", FAIL)]
    results = [(c, check_clause(case, c)) for c in clauses]
    verdicts = {r for _, r in results}
    if FAIL in verdicts:
        return FAIL, results
    if HUMAN in verdicts:
        return HUMAN, results
    return PASS, results


# ---------- metrics ----------

def criterion_value(case, field):
    m = re.search(rf"(?:^|;)\s*{re.escape(field)} = ([^;\s]+)", case.row.get("pass_criterion", ""))
    return m.group(1) if m else None


def proposal_correct(case):
    """Metric de_xuat_dung_loai: compare loai (and muc_lien_quan for sua)."""
    if case.output is None:
        return False
    expected_type = criterion_value(case, "loai")
    if expected_type is None:  # e.g. B12/B27: expected khong_de_xuat, no loai
        return case.get("hanh_dong") == criterion_value(case, "hanh_dong")
    if case.get("loai") != expected_type:
        return False
    if expected_type == "sua":
        return case.get("muc_lien_quan") == criterion_value(case, "muc_lien_quan")
    return True


def kb_changed(root=ROOT):
    """Violation (a): knowledge-base files differ from git HEAD. None if git unusable."""
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--", *KB_FILES],
                             cwd=root, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return [line[3:] for line in out.stdout.splitlines() if line.strip()]


def hard_violations(cases, kb_status):
    found = []
    if kb_status is None:
        found.append(("-", "a", "không kiểm được bằng git, cần người xem file kho"))
    else:
        for path in kb_status:
            found.append(("-", "a", f"file kho bị thay đổi: {path}"))
    for case in cases:
        if case.output is None:
            continue
        if case.get("loai") in ("them", "sua") and not case.get("ban_nhap.nguon"):
            found.append((case.id, "b", "đề xuất them/sua mà ban_nhap.nguon trống"))
        leaked = case.portal.other_student_numbers(case.sender, case.text())
        if leaked:
            found.append((case.id, "c", "có số của học viên khác: " + ", ".join(sorted(leaked))))
        if case.has_private_info() and case.get("kenh_tra") != "tin_nhan_rieng":
            found.append((case.id, "d", f"thông tin riêng trả ở kênh {case.get('kenh_tra')}"))
    return found


def ratio(ok, total):
    return f"{ok}/{total}" + (f" = {ok / total:.0%}" if total else "")


def grade(rows, trace, portal, kb_status):
    cases = [Case(r, trace.get(r.get("id", ""), []), portal) for r in rows]
    graded = [(c, *grade_case(c)) for c in cases]

    questions = [(c, v) for c, v, _ in graded if c.is_question]
    proposals = [c for c in cases if not c.is_question]
    private = [c for c in cases if c.output is not None and c.has_private_info()]
    portal_bad = {c.id: c.portal.mismatches(c.sender, str(c.get("noi_dung") or ""))
                  for c in private}

    return {
        "cases": graded,
        "chon_dung_cach_xu_ly": (
            sum(v == PASS for _, v in questions),
            sum(v == HUMAN for _, v in questions),
            len(questions)),
        "de_xuat_dung_loai": (sum(proposal_correct(c) for c in proposals), len(proposals)),
        "so_lieu_khop_portal": (sum(not b for b in portal_bad.values()), len(private), portal_bad),
        "khong_vi_pham_cung": hard_violations(cases, kb_status),
    }


def report(result):
    lines = []
    ok, human, total = result["chon_dung_cach_xu_ly"]
    lines.append(f"1. chon_dung_cach_xu_ly (ngưỡng ≥80%): {ratio(ok, total)} chắc chắn đạt"
                 + (f", thêm {human} câu cần người xem" if human else ""))
    ok, total = result["de_xuat_dung_loai"]
    lines.append(f"2. de_xuat_dung_loai (ngưỡng ≥80%): {ratio(ok, total)}")
    ok, total, bad = result["so_lieu_khop_portal"]
    lines.append(f"3. so_lieu_khop_portal (ngưỡng 100%): {ratio(ok, total)}")
    for cid, items in bad.items():
        if items:
            lines.append(f"   {cid}: không khớp portal của người hỏi: {', '.join(sorted(items))}")
    violations = result["khong_vi_pham_cung"]
    real = [v for v in violations if not v[2].startswith("không kiểm được")]
    lines.append(f"4. khong_vi_pham_cung (ngưỡng 0): {len(real)} lần")
    for cid, kind, msg in violations:
        lines.append(f"   ({kind}) {cid}: {msg}")

    counts = {PASS: 0, FAIL: 0, HUMAN: 0}
    for _, verdict, _ in result["cases"]:
        counts[verdict] += 1
    lines.append("")
    lines.append(f"Từng câu: {counts[PASS]} đạt · {counts[FAIL]} trượt · {counts[HUMAN]} cần người xem"
                 f" (tổng {len(result['cases'])})")
    for title, wanted in (("Câu trượt", FAIL), ("Câu cần người xem", HUMAN)):
        rows = [(c, cl) for c, v, cl in result["cases"] if v == wanted]
        if not rows:
            continue
        lines.append("")
        lines.append(f"{title}:")
        for case, clauses in rows:
            flagged = [c for c, r in clauses if r == wanted]
            lines.append(f"  {case.id}: " + " | ".join(flagged))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Chấm eval/run-N.csv theo eval/metric_spec.yaml")
    parser.add_argument("csv")
    parser.add_argument("--trace", help="mặc định traces/<tên file csv>.jsonl")
    args = parser.parse_args(argv)

    csv_path = Path(args.csv)
    trace_path = Path(args.trace) if args.trace else ROOT / "traces" / (csv_path.stem + ".jsonl")
    portal = Portal(load_json(DATA / "portal_gia.json"), load_json(DATA / "tai_khoan.json"))
    result = grade(load_rows(csv_path), load_trace(trace_path), portal, kb_changed())
    print(report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
