import unittest
import unittest.mock as mock

from sbankensheets.categorize import *
from sbankensheets.categorize import _categorize_uncertainty


class TestCategorize(unittest.TestCase):
    def setUp(self):
        super().setUp()
        # mock.patch("sbankensheets.gsheets.a1.A1Range").start()
        # mock.patch("sbankensheets.gsheets.google_sheets_helpers.find_cells").start()
        # mock.patch("sbankensheets.sbanken.transaction.Transaction").start()

    def tearDown(self):
        super().tearDown()
        mock.patch.stopall()

    def test_process_category_values_name_keywords(self):
        data = ["Dagligvare", "", "", "Rema, Kiwi"]
        expected = Category("Dagligvare", keywords=["rema", "kiwi"])
        actual = process_category_values(data)
        self.assertEqual(actual, expected)

    def test_process_category_values_name(self):
        data = ["Dagligvare"]
        expected = Category("Dagligvare")
        actual = process_category_values(data)
        self.assertEqual(actual, expected)

    def test_process_category_values_name_amount_keywords(self):
        data = ["Dagligvare", 20, "", "Rema, Kiwi"]
        expected = Category("Dagligvare", 20, keywords=["rema", "kiwi"])
        actual = process_category_values(data)
        self.assertEqual(actual, expected)

    def test_process_category_values_name_amount_amount_action_keywords(self):
        data = ["Dagligvare", 20, "+", "Rema, Kiwi"]
        expected = Category("Dagligvare", 20, "+", keywords=["rema", "kiwi"])
        actual = process_category_values(data)
        self.assertEqual(actual, expected)

    def test_process_category_values_no_name_raise_value_error(self):
        data = []
        self.assertRaises(ValueError, process_category_values, data)

    @mock.patch("sbankensheets.categorize._categorize.A1Range")
    @mock.patch("sbankensheets.categorize._categorize.find_cells")
    @mock.patch("sbankensheets.categorize._categorize.GSheet")
    def test_get_categories_find_no_cells_return_none(
        self, mock_gsheet, mock_find_cells, mock_a1range
    ):
        mock_find_cells.return_value = None
        self.assertIsNone(get_categories(mock_gsheet))

    @mock.patch("sbankensheets.categorize._categorize.A1Range")
    @mock.patch("sbankensheets.categorize._categorize.find_cells")
    @mock.patch("sbankensheets.categorize._categorize.GSheet")
    def test_get_categories_get_category_range_has_no_values_returns_none(
        self, mock_gsheet, mock_find_cells, mock_a1range
    ):
        mock_find_cells.return_value = (
            mock.MagicMock(),
            mock.MagicMock(),
            mock.MagicMock(),
        )
        mock_gsheet.get.return_value = {}
        self.assertIsNone(get_categories(mock_gsheet))

    @mock.patch("sbankensheets.categorize._categorize.process_category_values")
    @mock.patch("sbankensheets.categorize._categorize.A1Range")
    @mock.patch("sbankensheets.categorize._categorize.find_cells")
    @mock.patch("sbankensheets.categorize._categorize.GSheet")
    def test_get_categories_get_category_return_value(
        self, mock_gsheet, mock_find_cells, mock_a1range, mock_process
    ):
        expected = {"expenses": [0, 1], "income": [2, 3], "savings": [4, 5]}

        # Expenses, incomes and savings
        mock_find_cells.return_value = [mock.MagicMock() for _ in range(3)]
        # Number of categories
        mock_gsheet.get.return_value = {"values": [mock.MagicMock() for _ in range(2)]}
        # Values to be returned from process_category_values
        mock_process.side_effect = range(3 * 2)

        actual = get_categories(gsheet=mock_gsheet)
        self.assertEqual(actual, expected)

    def test_categorize_uncertainty_no_amount_action_equal_amount_return_true(self):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.amount = 100
        mock_category.amount = 100
        mock_category.amount_action = None

        self.assertTrue(_categorize_uncertainty(mock_transaction, mock_category))

    def test_categorize_uncertainty_no_amount_action_equal_amount_transaction_negative_return_true(
        self
    ):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.amount = -100
        mock_category.amount = 100
        mock_category.amount_action = None

        self.assertTrue(_categorize_uncertainty(mock_transaction, mock_category))

    def test_categorize_uncertainty_amount_action_plus_transaction_amount_more_than_category_amount_return_true(
        self
    ):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.amount = 100
        mock_category.amount = 50
        mock_category.amount_action = "+"

        self.assertTrue(_categorize_uncertainty(mock_transaction, mock_category))

    def test_categorize_uncertainty_amount_action_plus_transaction_amount_equal_category_amount_return_true(
        self
    ):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.amount = 100
        mock_category.amount = 100
        mock_category.amount_action = "+"

        self.assertTrue(_categorize_uncertainty(mock_transaction, mock_category))

    def test_categorize_uncertainty_amount_action_plus_transaction_amount_less_than_category_amount_return_false(
        self
    ):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.amount = 50
        mock_category.amount = 100
        mock_category.amount_action = "+"

        self.assertFalse(_categorize_uncertainty(mock_transaction, mock_category))

    def test_categorize_uncertainty_amount_action_minus_amount_less_than_category_amount_return_true(
        self
    ):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.amount = 50
        mock_category.amount = 100
        mock_category.amount_action = "-"

        self.assertTrue(_categorize_uncertainty(mock_transaction, mock_category))

    def test_categorize_uncertainty_amount_action_minus_amount_more_than_category_amount_return_false(
        self
    ):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.amount = 100
        mock_category.amount = 50
        mock_category.amount_action = "-"

        self.assertFalse(_categorize_uncertainty(mock_transaction, mock_category))

    def test_categorize_uncertainty_amount_action_minus_transaction_amount_equal_category_amount_return_true(
        self
    ):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.amount = 100
        mock_category.amount = 100
        mock_category.amount_action = "-"

        self.assertTrue(_categorize_uncertainty(mock_transaction, mock_category))

    def test_categorize_uncertainty_amount_action_not_plus_or_minus_return_false(self):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.amount = 50
        mock_category.amount_action = "any-value"

        self.assertFalse(_categorize_uncertainty(mock_transaction, mock_category))

    @mock.patch("sbankensheets.categorize._categorize._categorize_uncertainty")
    def test_categorize_with_uncertainty_keyword_calls_uncertainty(
        self, mock_uncertainty
    ):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.text.lower.return_value = "A string with test in it."
        mock_category.keywords = ["test?"]
        categorize(mock_transaction, [mock_category])

        mock_uncertainty.assert_called_once()

    @mock.patch("sbankensheets.categorize._categorize._categorize_uncertainty")
    def test_categorize_with_uncertainty_keyword_returns_category_name_if_uncertainty_true(
        self, mock_uncertainty
    ):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.text.lower.return_value = "A string with test in it."
        mock_category.keywords = ["test?"]
        test_name = "test-name"
        mock_category.name = test_name
        mock_uncertainty.return_value = True
        actual = categorize(mock_transaction, [mock_category])

        self.assertEqual(actual, test_name)

    def test_categorize_with_keyword_in_text_return_category_name(self):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.text.lower.return_value = "A string with test in it."
        mock_category.keywords = ["test"]
        test_name = "test-name"
        mock_category.name = test_name
        actual = categorize(mock_transaction, [mock_category])

        self.assertEqual(actual, test_name)

    def test_categorize_with_no_keyword_in_text_return_none(self):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.text.lower.return_value = "A string without keyword in it."
        mock_category.keywords = ["test"]
        test_name = "test-name"
        mock_category.name = test_name
        actual = categorize(mock_transaction, [mock_category])

        self.assertIsNone(actual)

    def test_categorize_with_star_keyword_return_category_name(self):
        mock_transaction = mock.MagicMock()
        mock_category = mock.MagicMock()
        mock_transaction.text.lower.return_value = "A string without keyword in it."
        mock_category.keywords = ["*"]
        test_name = "test-name"
        mock_category.name = test_name
        actual = categorize(mock_transaction, [mock_category])

        self.assertEqual(actual, test_name)

    def test_categorize_with_multiple_keywords_and_star_returns_ordinary_keyword_category_first(
        self
    ):
        mock_transaction = mock.MagicMock()
        mock_transaction.text.lower.return_value = "A string with test in it."

        mock_category_star = mock.MagicMock()
        mock_category_star.keywords = ["*"]
        test_name_star = "wrong-name"
        mock_category_star.name = test_name_star

        mock_category_ordinary = mock.MagicMock()
        mock_category_ordinary.keywords = ["test", "keywords"]
        test_name_ordinary = "correct-name"
        mock_category_ordinary.name = test_name_ordinary

        actual = categorize(
            mock_transaction, [mock_category_star, mock_category_ordinary]
        )

        self.assertEqual(actual, test_name_ordinary)
