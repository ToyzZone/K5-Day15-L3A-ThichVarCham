"""Write progress.html: a kanban board of the sub-issues of the task ticket (#21).

Run: python progress.py  (needs the `gh` CLI, logged in). Status comes only from GitHub:
closed as completed -> "Xong", open with the "đang làm" label -> "Đang làm", other open -> "Cần làm".
"""
import html
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

OWNER, REPO, PARENT = "ToyzZone", "K5-Day15-L3A-ThichVarCham", 21
DOING_LABEL = "đang làm"
NAMES = {"ToyzZone": "Thông", "ferr2764": "Hoàng", "hanhshi96": "Hạnh", "tuanhieu1162004-hub": "Hiếu"}
COLUMNS = [("todo", "Cần làm"), ("doing", "Đang làm"), ("done", "Xong")]
VN_TIME = timezone(timedelta(hours=7))

# ponytail: first 100 sub-issues only; add pageInfo paging if #21 ever grows past that.
QUERY = """query($owner: String!, $repo: String!, $parent: Int!) {
  repository(owner: $owner, name: $repo) { issue(number: $parent) { subIssues(first: 100) { nodes {
    number title url state stateReason
    assignees(first: 10) { nodes { login } }
    labels(first: 10) { nodes { name } }
    milestone { title dueOn }
  } } } }
}"""

CSS = """
:root{color-scheme:light dark;--bg:#f5f6f8;--col:#e9ecf0;--card:#fff;--line:#d5d9e0;--muted:#5f6673;--req:#b4232a}
@media (prefers-color-scheme:dark){:root{--bg:#15171b;--col:#1e2127;--card:#272b32;--line:#3a3f48;--muted:#9aa1ad;--req:#ff7b72}}
body{margin:0;padding:24px;font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg)}
h1{font-size:20px;margin:0 0 2px}
.sub{color:var(--muted);margin:0 0 16px}
.stats{display:flex;flex-wrap:wrap;gap:8px 28px;margin:0 0 20px;padding:0;list-style:none}
.stats progress{display:block;width:180px;margin-top:4px}
.board{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:start}
.col{background:var(--col);border-radius:10px;padding:12px}
.col h2{display:flex;justify-content:space-between;font-size:14px;margin:0 0 10px}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:8px;
  padding:10px;margin-top:8px;color:inherit;text-decoration:none}
.card:hover,.card:focus-visible{border-color:var(--muted)}
.num{color:var(--muted)}
.meta{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;font-size:12px;color:var(--muted)}
.meta span{border:1px solid var(--line);border-radius:4px;padding:0 6px}
.meta .req{color:var(--req);border-color:currentColor}
.done .card{opacity:.65}
@media (max-width:800px){.board{grid-template-columns:1fr}}
"""


def fetch():
    """Read the sub-issues of PARENT from GitHub with `gh api graphql`."""
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}",
         "-f", f"owner={OWNER}", "-f", f"repo={REPO}", "-F", f"parent={PARENT}"],
        check=True, capture_output=True, text=True, encoding="utf-8").stdout
    return json.loads(out)["data"]["repository"]["issue"]["subIssues"]["nodes"]


def board(issues):
    """Group issues into kanban columns; closed-not-completed (not planned, duplicate) are dropped."""
    cols = {key: [] for key, _ in COLUMNS}
    for i in issues:
        if i["state"] == "CLOSED":
            if i["stateReason"] == "COMPLETED":
                cols["done"].append(i)
        elif DOING_LABEL in {label["name"] for label in i["labels"]["nodes"]}:
            cols["doing"].append(i)
        else:
            cols["todo"].append(i)
    for items in cols.values():
        items.sort(key=lambda i: (_due(i), _milestone(i), i["number"]))
    return cols


def _milestone(i):
    return (i["milestone"] or {}).get("title") or "Chưa có mốc"


def _due(i):
    return (i["milestone"] or {}).get("dueOn") or "9999"


def _card(i):
    labels = [label["name"] for label in i["labels"]["nodes"] if label["name"] != DOING_LABEL]
    who = ", ".join(NAMES.get(a["login"], a["login"]) for a in i["assignees"]["nodes"]) or "chưa ai nhận"
    tags = [f'<span>{html.escape(_milestone(i).split(" · ")[0])}</span>']
    tags += [f'<span class="{"req" if n == "bắt buộc" else ""}">{html.escape(n)}</span>' for n in labels]
    tags.append(f"<span>{html.escape(who)}</span>")
    return (f'<a class="card" href="{html.escape(i["url"])}"><span class="num">#{i["number"]}</span> '
            f'{html.escape(i["title"])}<div class="meta">{"".join(tags)}</div></a>')


def render(issues, now):
    """Return the whole progress.html page for these issues, stamped with `now`."""
    cols = board(issues)
    kept = [i for items in cols.values() for i in items]
    stats = []
    for title in sorted({_milestone(i) for i in kept}, key=lambda t: min((_due(i), t) for i in kept if _milestone(i) == t)):
        group = [i for i in kept if _milestone(i) == title]
        done = sum(i in cols["done"] for i in group)
        stats.append(f'<li>{html.escape(title)}: <b>{done}/{len(group)}</b> xong'
                     f'<progress max="{len(group)}" value="{done}"></progress></li>')
    # one card per line so git diffs (and merge conflicts) stay readable
    columns = "\n".join(
        f'<section class="col {key}"><h2>{name}<span class="num">{len(cols[key])}</span></h2>\n'
        + "".join(_card(i) + "\n" for i in cols[key]) + "</section>"
        for key, name in COLUMNS)
    return (f'<!doctype html><html lang="vi"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Tiến độ · Thích Var Chạm</title><style>{CSS}</style></head><body>'
            f'<h1>Tiến độ nhóm Thích Var Chạm</h1>'
            f'<p class="sub">Ticket con của #{PARENT} · cập nhật {now:%H:%M %d/%m/%Y} (giờ Việt Nam) bằng '
            f'<code>python progress.py</code></p>'
            f'\n<ul class="stats">\n{"".join(s + chr(10) for s in stats)}</ul>\n'
            f'<div class="board">\n{columns}\n</div></body></html>\n')


if __name__ == "__main__":
    path = Path(__file__).with_name("progress.html")
    path.write_text(render(fetch(), datetime.now(VN_TIME)), encoding="utf-8")
    print(f"Đã ghi {path.name}")
