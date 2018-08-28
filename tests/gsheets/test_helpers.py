import unittest
import unittest.mock as mock

from sbankensheets.gsheets import filter_manual_cell_values, find_cells


class TestHelpers(unittest.TestCase):
    def setUp(self):
        super().setUp()

    @mock.patch("sbankensheets.gsheets._helpers.A1Range")
    def test_find_cells_get_no_values_return_none(self, mock_a1range):
        mock_gsheet = mock.MagicMock()
        mock_gsheet.get().get.return_value = None

        response = find_cells(mock_gsheet, mock.MagicMock(), mock.MagicMock())

        self.assertIsNone(response)

    @mock.patch("sbankensheets.gsheets._helpers.A1Range")
    def test_find_cells_calls_get_with_A1Range_sheet(self, mock_a1range):
        mock_gsheet = mock.MagicMock()
        mock_sheet = mock.Mock()

        find_cells(mock_gsheet, mock_sheet, mock.Mock())

        mock_gsheet.get.assert_called_once_with(mock_a1range(sheet=mock_sheet))

    @mock.patch("sbankensheets.gsheets._helpers.A1Cell")
    @mock.patch("sbankensheets.gsheets._helpers.A1Range")
    def test_find_cells_returns_correct_a1cells(self, mock_a1range, mock_a1cell):
        mock_gsheet = mock.MagicMock()
        mock_value = mock.MagicMock()

        expected_calls = [mock.call(0, 1), mock.call(2, 1)]
        mock_gsheet.get().get.return_value = [
            [mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()],
            [mock_value, mock.Mock(), mock_value, mock.Mock()],
            [mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()],
        ]

        response = find_cells(mock_gsheet, mock.Mock(), mock_value)
        self.assertEqual(expected_calls, mock_a1cell.call_args_list)

    @mock.patch("sbankensheets.gsheets._helpers.A1Cell")
    @mock.patch("sbankensheets.gsheets._helpers.A1Range")
    def test_find_cells_no_values_return_none(self, mock_a1range, mock_a1cell):
        mock_gsheet = mock.MagicMock()
        mock_value = mock.MagicMock()

        expected_calls = [mock.call(0, 1), mock.call(2, 1)]
        mock_gsheet.get().get.return_value = [
            [mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()],
            [mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()],
            [mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()],
        ]

        response = find_cells(mock_gsheet, mock.Mock(), mock_value)
        self.assertIsNone(response)

    def test_filter_manual_cell_values(self):
        manual_data = [mock.MagicMock() for _ in range(3)]
        for data in manual_data:
            data.__getitem__.return_value = "."
        automatic_data = [mock.MagicMock() for _ in range(4)]

        response = list(filter_manual_cell_values(manual_data + automatic_data))

        self.assertTrue(response == automatic_data)
