import unittest
import unittest.mock as mock

from sbankensheets.categorize import (
    process_category_values,
    get_categories,
    _categorize_uncertainty,
)


class TestCategorize(unittest.TestCase):
    def setUp(self):
        super().setUp()
        mock.patch("sbankensheets.gsheets.google_sheets.GSheet").start()
        mock.patch("sbankensheets.gsheets.a1.A1Range").start()
        mock.patch("sbankensheets.gsheets.google_sheets_helpers.find_cells").start()
        mock.patch("sbankensheets.sbanken.transaction.Transaction").start()

    def tearDown(self):
        super().tearDown()
        mock.patch.stopall()

    def test_process_category_value(self):
        test_category = "test_category"
        test_amount = "test_amount"
        default_amount = ""
        test_amount_action = "test_amount_action"
        default_amount_action = ""
        test_keywords = "test_keywords"
        default_keywords = []
        data = [test_category, test_amount, test_amount_action, test_keywords]

        for i in range(1, len(data) + 1):
            expected = {
                "category": test_category,
                "amount": test_amount if i > 1 else default_amount,
                "amount_action": test_amount_action if i > 2 else default_amount_action,
                "keywords": [test_keywords] if i > 3 else default_keywords,
            }
            actual = process_category_values(data[:i])
            self.assertEqual(actual, expected)
