import unittest

from expense_tracker.database import ExpenseDB


class TestExpenseDB(unittest.TestCase):
    def setUp(self):
        self.db = ExpenseDB(":memory:")  # temporary database, gone after each test

    def tearDown(self):
        self.db.close()

    def test_add_and_list(self):
        self.db.add(12.50, "Food", "lunch", "2026-09-01")
        rows = self.db.list()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["amount_cents"], 1250)
        self.assertEqual(rows[0]["category"], "food")

    def test_rejects_bad_amount(self):
        with self.assertRaises(ValueError):
            self.db.add(-5, "food")

    def test_rejects_bad_date(self):
        with self.assertRaises(ValueError):
            self.db.add(5, "food", spent_on="2026-13-99")

    def test_filter_by_category_and_month(self):
        self.db.add(10, "food", spent_on="2026-09-01")
        self.db.add(20, "travel", spent_on="2026-09-02")
        self.db.add(30, "food", spent_on="2026-08-15")
        self.assertEqual(len(self.db.list(category="food")), 2)
        self.assertEqual(len(self.db.list(month="2026-09")), 2)
        self.assertEqual(len(self.db.list(category="food", month="2026-09")), 1)

    def test_delete(self):
        expense_id = self.db.add(10, "food")
        self.assertTrue(self.db.delete(expense_id))
        self.assertFalse(self.db.delete(expense_id))

    def test_summary(self):
        self.db.add(10, "food")
        self.db.add(5.25, "food")
        self.db.add(40, "travel")
        self.assertEqual(self.db.summary(), [("travel", 4000), ("food", 1525)])


if __name__ == "__main__":
    unittest.main()