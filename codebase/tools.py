"""Tools of the Discord assistant; they match the tool table in spec.md §4.

Each tool is one @tool function. Data is read from data/ (described in data/DATA_CARD.md).
No tool writes to the knowledge base: an entry takes effect only after a lab coach approves it.

The knowledge base has TWO TABLES:
    data/kho_co_dinh.json   fixed table: information that stays the same across cohorts. Lab coaches never edit it.
    data/kho_theo_khoa.json course table: information for the running cohort. Every approved proposal goes here.
When the two tables disagree, the course table wins: a course entry with "ghi_de" hides the entry it overrides.

Tool names, their inputs and the JSON keys they return stay in Vietnamese: the trace records tool names
and the locked metric (eval/metric_spec.yaml) refers to them.
"""
import contextvars
import json
import os
import re

from tracing import tool, TOOLS  # noqa: F401

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Student id of the person asking. Code sets it from the sending account (agent.py); the model has no way
# to change it, because no tool takes a student id as a parameter.
ASKER_ID = contextvars.ContextVar("asker_id", default=None)
RUNTIME_KB = contextvars.ContextVar("runtime_kb", default=None)

PORTAL_ITEMS = ("xp", "diem_danh", "daily_standup", "gate", "deadline", "coach_phu_trach")


def _load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def find_account(discord_id):
    """Look up a Discord account → role and student id. Not a model tool."""
    return next((t for t in _load("tai_khoan.json") if t["discord_id"] == discord_id), None)


# ponytail: keyword overlap. Switch to embeddings when eval fails because a search misses.
_STOPWORDS = set("là khi nào ạ mình bạn có được không thì và ở của cho với nhỉ vậy đi giúp à nhé các em".split())


def _words(text):
    return {t for t in re.findall(r"\w+", text.lower()) if t not in _STOPWORDS and len(t) > 1}


def _rank(query, items, text_of, k=3):
    wanted = _words(query)
    scored = sorted(((len(wanted & _words(text_of(m))), m) for m in items), key=lambda x: -x[0])
    return [m for score, m in scored[:k] if score >= 2]


def seed_knowledge():
    """Both seed tables, each entry tagged with its table. The Discord layer seeds the running knowledge base with it."""
    return ([dict(m, bang="theo_khoa") for m in _load("kho_theo_khoa.json")]
            + [dict(m, bang="co_dinh") for m in _load("kho_co_dinh.json")])


def _live_entries():
    """Merge the two tables. Code decides precedence: a course entry hides the entry it overrides."""
    runtime = RUNTIME_KB.get()  # the Discord layer passes the running knowledge base (SQLite); eval reads the seed files
    entries = runtime if runtime is not None else seed_knowledge()
    live = [m for m in entries if m["trang_thai"] == "hieu_luc"]
    course = [m for m in live if m.get("bang") == "theo_khoa"]
    fixed = [m for m in live if m.get("bang") != "theo_khoa"]
    hidden = {m.get("ghi_de") for m in course}
    return [m for m in course + fixed if m["ma"] not in hidden]


@tool
def tra_kho_kien_thuc(question: str) -> list:
    """Search the knowledge base, both the fixed and the course table (live entries only).
    Input: question (str). Output: up to 3 entries {"ma", "bang", "cau_hoi", "tra_loi", "nguon"}; [] if none.
    A fixed entry overridden by a course entry is never returned. No external effect."""
    entries = _live_entries()
    return [{k: m[k] for k in ("ma", "bang", "cau_hoi", "tra_loi", "nguon", "pham_vi") if k in m}
            for m in _rank(question, entries, lambda m: m["cau_hoi"] + " " + m["tra_loi"])]


@tool
def tra_thong_bao(question: str) -> list:
    """Search the course's official announcements.
    Input: question (str). Output: up to 3 announcements {"ma", "ngay", "noi_dung", "link"}; [] if none.
    No external effect."""
    return _rank(question, _load("thong_bao.json"), lambda m: m["noi_dung"])


@tool
def tra_portal(item: str) -> dict:
    """Look up one private item of the ASKER THEMSELVES on the fake portal.
    Input: item name, one of xp · diem_danh · daily_standup · gate · deadline · coach_phu_trach.
    Output: {"muc", "du_lieu"} or {"loi"}. No external effect.
    Still fake at CP2: reads data/portal_gia.json directly; after CP2 it goes through MCP."""
    student_id = ASKER_ID.get()
    profile = _load("portal_gia.json").get(student_id) if student_id else None
    if profile is None:
        return {"loi": "không xác định được người hỏi"}
    if item not in PORTAL_ITEMS:
        return {"loi": "không có mục %r; chỉ có: %s" % (item, ", ".join(PORTAL_ITEMS))}
    return {"muc": item, "du_lieu": profile[item]}


@tool
def tao_ticket(summary: str) -> dict:
    """Draft a Discord ticket to a lab coach (how a question is handed to a person).
    Input: question summary (str). Output: {"trang_thai": "cho_hoc_vien_xac_nhan", "tom_tat"}.
    Has an external effect (opens a ticket, notifies the lab coach), so the tool only DRAFTS:
    the ticket is created only when the student presses confirm."""
    return {"trang_thai": "cho_hoc_vien_xac_nhan", "tom_tat": summary}
