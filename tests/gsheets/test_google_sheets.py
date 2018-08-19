import unittest
import unittest.mock as mock

from sbankenssheets.gsheets import GSheets, A1Cell, A1Range


class TestGSheets(unittest.TestCase):

    def setUp(self):
        super().setUp()
        mock.patch('sbankenssheets.gsheets.google_sheets.build').start()
        mock.patch('sbankenssheets.gsheets.google_sheets.Http').start()
        mock.patch('sbankenssheets.gsheets.google_sheets.file').start()
        mock.patch('sbankenssheets.gsheets.google_sheets.client').start()
        mock.patch('sbankenssheets.gsheets.google_sheets.tools').start()

        self.gsheets = GSheets('some-id')

    def tearDown(self):
        super().tearDown()
        mock.patch.stopall()

    def test_call_serivce_get_with_correct_args(self):
        range = 'A1:C5'
        self.gsheets.get(range)

        self.gsheets.service.spreadsheets().values().get.assert_called_with(
            range=range,
            spreadsheetId=self.gsheets.spreadsheet_id
        )

    def test_call_serivce_get_execute_called_once(self):
        range = 'A1:C5'
        self.gsheets.get(range)

        self.gsheets.service.spreadsheets().values().get().execute.assert_called_once()

    def test_call_serivce_append_with_correct_args(self):
        range = 'A1:B2'
        values = [['key1', 'value1'], ['key2', 'value2']]
        self.gsheets.append(
            range=range,
            values=values
        )

        self.gsheets.service.spreadsheets().values().append.assert_called_with(
            spreadsheetId=self.gsheets.spreadsheet_id,
            range=range,
            valueInputOption='USER_ENTERED',
            insertDataOption='OVERWRITE',
            body={
                'range': range,
                'values': values
            }
        )

class TestA1Cell(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.cell_c4 = A1Cell('C4')

    def test_add_two_cells(self):
        addition = (1, 2)
        expected = A1Cell('D6')

        actual = self.cell_c4 + addition

        self.assertEqual(actual, expected)

    def test_add_with_non_tuple_raises_exception(self):
        import operator

        for addition in (5, 5.4, 'A5', A1Cell('A5')):
            self.assertRaises(ValueError, operator.add, self.cell_c4, addition)

    def test_iadd_two_cells(self):
        addition = (1, 2)
        expected = A1Cell('D6')

        self.cell_c4 += addition
        actual = self.cell_c4

        self.assertEqual(actual, expected)

    def test_get_index_0(self):
        expected_0_idx = 'C'
        actual_0_idx = self.cell_c4[0]

        self.assertEqual(actual_0_idx, expected_0_idx)

    def test_get_index_1(self):
        expected_1_idx = '4'
        actual_1_idx = self.cell_c4[1]

        self.assertEqual(actual_1_idx, expected_1_idx)

    def test_get_index_not_0_or_1_raises_index_error(self):
        indices = (-1, 2, 100)

        for idx in indices:
            self.assertRaises(IndexError, self.cell_c4.__getitem__, idx)

    def test_set_index_not_0_or_1_raises_index_error(self):
        indices = (-1, 2, 100)

        for idx in indices:
            self.assertRaises(IndexError, self.cell_c4.__getitem__, idx)

    def test_set_index_0_with_str_correct(self):
        values = ['A', 'a', 'B', 'b', 'Z', 'z']
        expected_values = [A1Cell(f'{value.upper()}4') for value in values]

        for value, expected in zip(values, expected_values):
            self.cell_c4[0] = value
            self.assertEqual(self.cell_c4, expected)

    def test_set_index_0_with_int_correct(self):
        values = [0, 1, 25]
        expected_values = [A1Cell(f'{chr(ord("A")+value)}4') for value in values]

        for value, expected in zip(values, expected_values):
            self.cell_c4[0] = value
            self.assertEqual(self.cell_c4, expected)

    def test_set_index_0_value_above_25_raises_value_error(self):
        values = [-1, 26, 100]

        for value in values:
            self.assertRaises(ValueError, self.cell_c4.__setitem__, 0, value)

    def test_set_index_0_value_non_a_to_z_raises_value_error(self):
        for value in ('AA', 'Æ', '$', '0', '12'):
            self.assertRaises(ValueError, self.cell_c4.__setitem__, 0, value)

    def test_set_index_1_with_positive_int_correct(self):
        values = [0, 1, 100, int(1e6)]

        expected_values = [A1Cell(f'C{value+1}') for value in values]

        for value, expected in zip(values, expected_values):
            self.cell_c4[1] = value
            self.assertEqual(self.cell_c4, expected)

    def test_set_index_1_with_negative_int_raise_value_error(self):
        for value in (-1, int(-1e6)):
            self.assertRaises(ValueError, self.cell_c4.__setitem__, 1, value)

    def test_set_index_1_with_non_int_raise_value_error(self):
        for value in (-1.1, 0.3, 1e1, '1', 'hei', (0, 1)):
            self.assertRaises(ValueError, self.cell_c4.__setitem__, 1, value)


class TestA1Range(unittest.TestCase):

    def setUp(self):
        self.cell_b5 = A1Cell('B5')
        self.cell_c6 = A1Cell('C6')
        self.range_b5_c6 = A1Range(self.cell_b5, self.cell_c6)

    def test_init_with_range(self):
        actual = A1Range(self.cell_b5, range=(1, 1))
        self.assertEqual(actual, self.range_b5_c6)

    def test_init_with_one_arument_raise_value_error(self):
        self.assertRaises(ValueError, A1Range, self.cell_b5)

    def test_init_with_end_cell_and_range_raise_value_error(self):
        self.assertRaises(ValueError,
                          A1Range,
                          self.cell_b5,
                          end_cell=self.cell_c6,
                          range=(1, 1))

    def test_str_format(self):
        self.assertEqual(str(self.range_b5_c6), 'B5:C6')

    def test_get_0_idx(self):
        actual = self.range_b5_c6[0]
        self.assertEqual(actual, self.cell_b5)

    def test_get_1_idx(self):
        actual = self.range_b5_c6[1]
        self.assertEqual(actual, self.cell_c6)

