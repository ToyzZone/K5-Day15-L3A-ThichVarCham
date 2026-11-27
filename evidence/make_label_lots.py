"""Split Kute's answered turns into labelling lots for human review.

Usage:
    python evidence/make_label_lots.py evidence/discord/raw-sach-2026-11-27.jsonl evidence/discord

Pool: every turn where Kute replied to a person with actual content, i.e. not a
ticket menu, not a timeout, not a bare "@Mod" hand-off and not a clarifying menu
("mô tả rõ hơn"). The pool is shuffled once with a fixed seed. The first OVERLAP
rows go to every lot (to measure agreement); the rest are dealt round-robin.
Because of the shuffle, any prefix a labeller finishes is a random sample.

Lots contain real (pseudonymised) Discord text: they are written as raw-lo-N.json
so the repo's .gitignore (evidence/**/raw-*) keeps them out of git.
"""
import json
import random
import re
import sys
from datetime import datetime, timedelta, timezone

SEED = 2711
LOTS = 4
OVERLAP = 20
VN = timezone(timedelta(hours=7))
PERSON_CODE = re.compile(r"@?\bP\d+\b")


def is_bot(row):
    return (row["a"] or "").startswith("BOT:")


def has_content(row):
    """True when Kute's reply carries an answer a person can judge."""
    text = row["text"] or ""
    if "request timeout" in text:
        return False
    if not text.strip():  # ticket menu or embed-only reply
        return False
    if text.lstrip().startswith("@Mod"):  # bare hand-off
        return False
    if "mô tả rõ hơn" in text:  # clarifying menu
        return False
    return True


def squash(text):
    return re.sub(r"\s+", " ", text or "").strip()


def hide_people(text):
    return PERSON_CODE.sub("@[ai đó]", text or "")


def build_pool(rows):
    by_author = {}
    for row in rows:
        if row["a"] and not is_bot(row):
            by_author.setdefault(row["a"], []).append(row)
    pool = []
    for row in rows:
        reply_to = row.get("r") or {}
        if not (is_bot(row) and (reply_to.get("a") or "").startswith("P") and has_content(row)):
            continue
        prefix = squash(reply_to.get("t"))[:60]
        question = reply_to.get("t") or ""
        for earlier in reversed([q for q in by_author.get(reply_to["a"], []) if q["t"] <= row["t"]]):
            if prefix and squash(earlier["text"]).startswith(prefix):
                question = earlier["text"]
                break
        asked = datetime.fromisoformat(row["t"].replace("Z", "+00:00")).astimezone(VN)
        pool.append({
            "id": row["id"][-8:],
            "asked_at": asked.strftime("%d/%m/%Y %H:%M"),
            "question": hide_people(question),
            "answer": hide_people(row["text"]),
            "attachment": hide_people(row["emb"]),
        })
    return pool


def deal(pool, seed=SEED, lots=LOTS, overlap=OVERLAP):
    shuffled = pool[:]
    random.Random(seed).shuffle(shuffled)
    shared, rest = shuffled[:overlap], shuffled[overlap:]
    return [shared + rest[i::lots] for i in range(lots)]


def main(src, out_dir):
    rows = [json.loads(line) for line in open(src, encoding="utf-8")]
    pool = build_pool(rows)
    for number, items in enumerate(deal(pool), start=1):
        lot = {"lot": number, "seed": SEED, "overlap": OVERLAP, "pool_size": len(pool), "items": items}
        path = f"{out_dir}/raw-lo-{number}.json"
        json.dump(lot, open(path, "w", encoding="utf-8"), ensure_ascii=False)
        print(path, len(items))
    print("pool", len(pool), "seed", SEED, "overlap", OVERLAP)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
