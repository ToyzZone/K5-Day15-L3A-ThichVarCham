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

    def test_one_column_per_person_with_own_count(self):
        page = progress.render([issue(1, "CLOSED", "COMPLETED", who=["ToyzZone"]), issue(2, who=["ToyzZone"]),
                                issue(3, who=["hanhshi96"]), issue(4)], datetime(2026, 11, 27))
        self.assertIn('<section class="who p0"><h2>Thông<span class="num">1/2 xong</span></h2>', page)
        # the colour class follows the position in NAMES, not the rendered column index
        self.assertIn('<section class="who p2"><h2>Hạnh<span class="num">0/1 xong</span></h2>', page)
        self.assertIn('<section class="who"><h2>Chưa ai nhận<span class="num">0/1 xong</span></h2>', page)

    def test_shared_ticket_sits_under_each_assignee_but_counts_once_per_milestone(self):
        page = progress.render([issue(1, "CLOSED", "COMPLETED", who=["ToyzZone", "ferr2764"]),
                                issue(2, who=["ToyzZone"])], datetime(2026, 11, 27))
        self.assertEqual(page.count('href="https://github.com/x/issues/1"'), 2)
        self.assertIn(f"{CP3[0]}: <b>1/2</b> xong", page)
        self.assertIn("<span>Thông, Hoàng</span>", page)

    def test_status_groups_inside_a_person_skip_empty_ones(self):
        page = progress.render([issue(1, "CLOSED", "COMPLETED", who=["ToyzZone"]),
                                issue(2, labels=["đang làm"], who=["ToyzZone"])], datetime(2026, 11, 27))
        self.assertLess(page.index(">Đang làm<"), page.index(">Xong<"))
        self.assertNotIn(">Cần làm<", page)
        self.assertIn('<a class="card doing" href="https://github.com/x/issues/2">', page)

    def test_unknown_login_heading_is_escaped(self):
        page = progress.render([issue(1, who=["<i>x"])], datetime(2026, 11, 27))
        self.assertIn('<section class="who"><h2>&lt;i&gt;x<span', page)


class PeopleTest(unittest.TestCase):
    def test_team_order_then_other_logins_then_unassigned(self):
        groups = progress.people([issue(1), issue(2, who=["someone"]), issue(3, who=["hanhshi96"]),
                                  issue(4, who=["hanhshi96", "ToyzZone"])])
        self.assertEqual([(who, [i["number"] for i in items]) for who, items in groups.items()],
                         [("ToyzZone", [4]), ("hanhshi96", [3, 4]), ("someone", [2]), (None, [1])])


if __name__ == "__main__":
    unittest.main()
