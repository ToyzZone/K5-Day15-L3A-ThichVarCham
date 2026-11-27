"""Merge label files exported by evidence/label-tool.html and print a Markdown summary.

Usage:
    python evidence/merge_labels.py evidence/discord/raw-nhan-lo-*.json

Each item counts once. An item labelled by several people takes the majority
label; a tie becomes "khong_chac". Agreement is reported on items labelled by
at least two people.
"""
import collections
import json
import sys

LABELS = ["dung", "sai", "lac_de", "da_cu", "khong_tra_loi", "khong_chac"]
NAMES = {
    "dung": "Đúng",
    "sai": "Sai",
    "lac_de": "Lạc đề",
    "da_cu": "Đã cũ",
    "khong_tra_loi": "Không trả lời",
    "khong_chac": "Không chắc",
}


def collect(exports):
    """Return {item_id: {labeller: label}} from a list of export dicts."""
    votes = collections.defaultdict(dict)
    for export in exports:
        labeller = f"{export.get('labeler') or 'lô'}#{export.get('lot')}"
        for entry in export.get("labels", []):
            if entry.get("label") in LABELS:
                votes[entry["id"]][labeller] = entry["label"]
    return votes


def majority(labels):
    ranked = collections.Counter(labels).most_common()
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return "khong_chac"
    return ranked[0][0]


def summarise(votes):
    final = collections.Counter(majority(list(v.values())) for v in votes.values())
    shared = [list(v.values()) for v in votes.values() if len(v) >= 2]
    unanimous = sum(1 for labels in shared if len(set(labels)) == 1)
    return {"items": len(votes), "final": final, "shared": len(shared), "unanimous": unanimous}


def to_markdown(summary):
    n = summary["items"]
    lines = [f"Số câu đã gán: {n}", "", "| Nhãn | x / n | % |", "|---|---|---|"]
    for label in LABELS:
        x = summary["final"][label]
        lines.append(f"| {NAMES[label]} | {x}/{n} | {100 * x / n:.0f}% |" if n else f"| {NAMES[label]} | 0/0 | |")
    judged = n - summary["final"]["khong_chac"] - summary["final"]["khong_tra_loi"]
    bad = summary["final"]["sai"] + summary["final"]["lac_de"] + summary["final"]["da_cu"]
    if judged:
        lines += ["", f"Trong {judged} câu chấm được đúng sai: {bad} câu không dùng được ({100 * bad / judged:.0f}%)."]
    if summary["shared"]:
        lines += ["", f"Câu có từ 2 người gán: {summary['shared']}; mọi người gán giống nhau ở {summary['unanimous']} câu "
                      f"({100 * summary['unanimous'] / summary['shared']:.0f}%)."]
    return "\n".join(lines)


if __name__ == "__main__":
    loaded = [json.load(open(path, encoding="utf-8")) for path in sys.argv[1:]]
    print(to_markdown(summarise(collect(loaded))))
