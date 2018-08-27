import unittest
import unittest.mock as mock

from sbankensheets.categorize import process_category_values, get_categories, Category


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
