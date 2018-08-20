import unittest
import unittest.mock as mock

from sbankensheets.gsheets import GSheet, A1Cell, A1Range


class TestGSheet(unittest.TestCase):

    def setUp(self):
        super().setUp()
        mock.patch('sbankensheets.gsheets.google_sheets.build').start()
        mock.patch('sbankensheets.gsheets.google_sheets.Http').start()
        mock.patch('sbankensheets.gsheets.google_sheets.file').start()
        mock.patch('sbankensheets.gsheets.google_sheets.client').start()
        mock.patch('sbankensheets.gsheets.google_sheets.tools').start()

        self.gsheets = GSheet('some-id')

    def tearDown(self):
        super().tearDown()
        mock.patch.stopall()

    def test_get_calls_service_get_with_correct_args(self):
        range = 'A1:C5'
        self.gsheets.get(range)

        self.gsheets.service.spreadsheets().values().get.assert_called_once_with(
            range=range,
            spreadsheetId=self.gsheets.spreadsheet_id
        )

    def test_get_calls_service_get_execute_once(self):
        range = 'A1:C5'
        self.gsheets.get(range)

        self.gsheets.service.spreadsheets().values().get().execute.assert_called_once()

    def test_append_calls_service_append_with_correct_args(self):
        range = 'A1:B2'
        values = [['key1', 'value1'], ['key2', 'value2']]
        self.gsheets.append(
            range=range,
            values=values
        )

        self.gsheets.service.spreadsheets().values().append.assert_called_once_with(
            spreadsheetId=self.gsheets.spreadsheet_id,
            range=range,
            valueInputOption='USER_ENTERED',
            insertDataOption='OVERWRITE',
            body={
                'range': range,
                'values': values
            }
        )

    def test_append_calls_service_append_execute_once(self):
        range = 'A1:B2'
        values = [['key1', 'value1'], ['key2', 'value2']]
        self.gsheets.append(
            range=range,
            values=values
        )

        self.gsheets.service.spreadsheets().values().append().execute.assert_called_once()

    def test_get_batch_calls_service_getBatch_with_correct_args(self):
        ranges = ['A1:C5', 'A5:C7']
        self.gsheets.get_batch(ranges)

        self.gsheets.service.spreadsheets().values().batchGet.assert_called_once_with(
            ranges=ranges,
            spreadsheetId=self.gsheets.spreadsheet_id
        )

    def test_get_batch_calls_service_getBatch_execute_one(self):
        ranges = ['A1:C5', 'A5:C7']
        self.gsheets.get_batch(ranges)

        self.gsheets.service.spreadsheets().values().batchGet().execute.assert_called_once()


