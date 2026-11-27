import unittest
from datetime import datetime

import progress

CP3 = ("CP3 · 10:00 Thứ Bảy 28/11", "2026-11-27T00:00:00Z")
FINAL = ("Nộp cuối · 23:59 Thứ Bảy 28/11", "2026-11-28T00:00:00Z")


def issue(n, state="OPEN", reason=None, labels=(), who=(), milestone=CP3, title="việc"):
    return {"number": n, "title": title, "url": f"https://github.com/x/issues/{n}",
            "state": state, "stateReason": reason,
            "assignees": {"nodes": [{"login": w} for w in who]},
            "labels": {"nodes": [{"name": name} for name in labels]},
            "milestone": {"title": milestone[0], "dueOn": milestone[1]}}


class BoardTest(unittest.TestCase):
    def test_columns_follow_github_state_and_label(self):
        cols = progress.board([issue(1), issue(2, labels=["đang làm"]), issue(3, "CLOSED", "COMPLETED"),
                               issue(4, "CLOSED", "NOT_PLANNED"), issue(5, "CLOSED", "DUPLICATE")])
        self.assertEqual({k: [i["number"] for i in v] for k, v in cols.items()},
                         {"todo": [1], "doing": [2], "done": [3]})

    def test_cards_sorted_by_due_date_then_number(self):
        cols = progress.board([issue(9, milestone=FINAL), issue(7), issue(3)])
        self.assertEqual([i["number"] for i in cols["todo"]], [3, 7, 9])


class RenderTest(unittest.TestCase):
    def test_escapes_titles_and_shows_names(self):
        page = progress.render([issue(5, title="<script>x</script>", who=["ferr2764", "someone"])],
                               datetime(2026, 11, 27, 22, 5))
        self.assertNotIn("<script>x", page)
        self.assertIn("&lt;script&gt;x&lt;/script&gt;", page)
        self.assertIn("Hoàng, someone", page)
        self.assertIn("22:05 27/11/2026", page)

    def test_milestone_progress_counts_done_over_kept(self):
        page = progress.render([issue(1, "CLOSED", "COMPLETED"), issue(2), issue(3, "CLOSED", "NOT_PLANNED")],
                               datetime(2026, 11, 27))
        self.assertIn("<b>1/2</b> xong", page)


if __name__ == "__main__":
    unittest.main()
