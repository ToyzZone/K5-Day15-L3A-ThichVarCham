"""Write progress.html: the sub-issues of the task ticket (#21), one column per assignee.

Run: python progress.py  (needs the `gh` CLI, logged in). Status comes only from GitHub:
closed as completed -> "Xong", open with the "đang làm" label -> "Đang làm", other open -> "Cần làm".
Inside a column the tickets are grouped by status; a ticket with several assignees shows under each.
"""
import html
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

OWNER, REPO, PARENT = "ToyzZone", "K5-Day15-L3A-ThichVarCham", 21
DOING_LABEL = "đang làm"
NAMES = {"ToyzZone": "Thông", "ferr2764": "Hoàng", "hanhshi96": "Hạnh", "tuanhieu1162004-hub": "Hiếu"}
STATUSES = [("doing", "Đang làm"), ("todo", "Cần làm"), ("done", "Xong")]  # order inside a person's column
UNASSIGNED = "Chưa ai nhận"
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

# ponytail: one hue per NAMES position (.p0-.p3); a fifth member falls back to grey until .p4 is added.
CSS = """
:root{color-scheme:light dark;--bg:#f5f6f8;--col:#e9ecf0;--card:#fff;--line:#d5d9e0;--muted:#5f6673;--req:#b4232a;
  --who:48% .16;--todo:#8a93a3;--doing:#c27c0e;--done:#2e9a52}
@media (prefers-color-scheme:dark){:root{--bg:#15171b;--col:#1e2127;--card:#272b32;--line:#3a3f48;--muted:#9aa1ad;
  --req:#ff7b72;--who:78% .13;--todo:#737c8a;--doing:#e3b341;--done:#56d364}}
body{margin:0;padding:24px;font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg)}
h1{font-size:20px;margin:0 0 2px}
.sub{color:var(--muted);margin:0 0 16px}
.stats{display:flex;flex-wrap:wrap;gap:8px 28px;margin:0 0 20px;padding:0;list-style:none}
.stats progress{display:block;width:180px;height:8px;margin-top:6px;appearance:none;border:0;border-radius:4px;
  overflow:hidden;background:var(--line)}
.stats progress::-webkit-progress-bar{background:var(--line)}
.stats progress::-webkit-progress-value{background:var(--done)}
.stats progress::-moz-progress-bar{background:var(--done)}
.board{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;align-items:start}
.who{--c:var(--muted);background:color-mix(in oklch,var(--c) 16%,var(--col));border-top:4px solid var(--c);
  border-radius:10px;padding:12px}
.p0{--c:oklch(var(--who) 255)}.p1{--c:oklch(var(--who) 305)}.p2{--c:oklch(var(--who) 350)}.p3{--c:oklch(var(--who) 200)}
.who h2{display:flex;justify-content:space-between;align-items:baseline;font-size:16px;margin:0;color:var(--c)}
.who h2 .num{font-size:12px;font-weight:400}
.who h3{display:flex;align-items:center;gap:6px;font-size:12px;margin:14px 0 0;color:var(--muted)}
.who h3::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--s)}
.todo{--s:var(--todo)}.doing{--s:var(--doing)}.done{--s:var(--done)}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:8px;
  box-shadow:inset 4px 0 var(--s);padding:10px 10px 10px 14px;margin-top:8px;color:inherit;text-decoration:none}
.card:hover,.card:focus-visible{border-color:var(--muted)}
.card.done{opacity:.65}
.num{color:var(--muted)}
.meta{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;font-size:12px;color:var(--muted)}
.meta span{border:1px solid var(--line);border-radius:4px;padding:0 6px}
.meta .req{color:var(--req);border-color:currentColor}
"""


def fetch():
    """Read the sub-issues of PARENT from GitHub with `gh api graphql`."""
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}",
         "-f", f"owner={OWNER}", "-f", f"repo={REPO}", "-F", f"parent={PARENT}"],
        check=True, capture_output=True, text=True, encoding="utf-8").stdout
    return json.loads(out)["data"]["repository"]["issue"]["subIssues"]["nodes"]


def board(issues):
    """Group issues by status; closed-not-completed (not planned, duplicate) are dropped."""
    cols = {key: [] for key, _ in STATUSES}
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


def people(issues):
    """Group issues by assignee login: team order, then other logins, then unassigned (key None) last.

    A ticket with several assignees appears under each of them.
    """
    groups = {login: [] for login in NAMES}
    for i in issues:
        for login in [a["login"] for a in i["assignees"]["nodes"]] or [None]:
            groups.setdefault(login, []).append(i)
    groups[None] = groups.pop(None, [])
    return {login: items for login, items in groups.items() if items}


def _milestone(i):
    return (i["milestone"] or {}).get("title") or "Chưa có mốc"


def _due(i):
    return (i["milestone"] or {}).get("dueOn") or "9999"


def _card(i, status):
    labels = [label["name"] for label in i["labels"]["nodes"] if label["name"] != DOING_LABEL]
    tags = [f'<span>{html.escape(_milestone(i).split(" · ")[0])}</span>']
    tags += [f'<span class="{"req" if n == "bắt buộc" else ""}">{html.escape(n)}</span>' for n in labels]
    who = [NAMES.get(a["login"], a["login"]) for a in i["assignees"]["nodes"]]
    if len(who) > 1:  # the column already names a sole assignee
        tags.append(f'<span>{html.escape(", ".join(who))}</span>')
    return (f'<a class="card {status}" href="{html.escape(i["url"])}"><span class="num">#{i["number"]}</span> '
            f'{html.escape(i["title"])}<div class="meta">{"".join(tags)}</div></a>')


def _person(login, issues):
    """One column: the person's name and done count, then their cards grouped by status."""
    cols = board(issues)
    colour = f" p{list(NAMES).index(login)}" if login in NAMES else ""
    # one card per line so git diffs (and merge conflicts) stay readable
    groups = "".join(
        f'<h3 class="{key}">{label}<span class="num">{len(cols[key])}</span></h3>\n'
        + "".join(_card(i, key) + "\n" for i in cols[key])
        for key, label in STATUSES if cols[key])
    return (f'<section class="who{colour}"><h2>{html.escape(NAMES.get(login, login) or UNASSIGNED)}'
            f'<span class="num">{len(cols["done"])}/{sum(map(len, cols.values()))} xong</span></h2>\n{groups}</section>')


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
    columns = "\n".join(_person(login, items) for login, items in people(kept).items())
    return (f'<!doctype html><html lang="vi"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Tiến độ · Thích Var Chạm</title><style>{CSS}</style></head><body>'
            f'<h1>Tiến độ nhóm Thích Var Chạm</h1>'
            f'<p class="sub">Ticket con của #{PARENT}, mỗi người một cột (ticket chung hiện ở cột của từng người)'
            f' · cập nhật {now:%H:%M %d/%m/%Y} (giờ Việt Nam) bằng '
            f'<code>python progress.py</code></p>'
            f'\n<ul class="stats">\n{"".join(s + chr(10) for s in stats)}</ul>\n'
            f'<div class="board">\n{columns}\n</div></body></html>\n')


if __name__ == "__main__":
    path = Path(__file__).with_name("progress.html")
    path.write_text(render(fetch(), datetime.now(VN_TIME)), encoding="utf-8")
    print(f"Đã ghi {path.name}")
