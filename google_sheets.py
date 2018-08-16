from typing import List, Dict, Tuple, Union, Iterable

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import google_sheets_helpers as gsh


class GSheets(object):

    @staticmethod
    def _create_authenticated_google_service():
        SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('sheets', 'v4', http=creds.authorize(Http()))
        return service

    def __init__(self, spreadsheet_id: str):
        self.service = GSheets._create_authenticated_google_service()
        self.spreadsheet_id = spreadsheet_id

    def get(self, range):
        return self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range
        ).execute()

    def append(self,
               range: str,
               values: List[List[str]],
               value_input_option: str = 'USER_ENTERED',
               insert_data_option: str = 'OVERWRITE', ) -> Dict:
        return self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body={
                'range': range,
                'values': values
            }
        ).execute()

    def get_batch(self, ranges: List[str]):
        return self.service.spreadsheets().values().getBatch(
            spreadsheetId=self.spreadsheet_id,
            ranges=ranges
        ).execute()

    def clear(self):
        raise NotImplementedError


class A1Cell(object):

    def __init__(self, *args: Union[Union[List[int, int], Tuple[int, int]], 'A1Cell', int]):

        if len(args) == 1 and (isinstance(args, (A1Cell, tuple))):
            if isinstance(args, A1Cell):
                self._initialize_from_cell(args)
            elif isinstance(args, (tuple, list)) and len(args) == 2 and all((isinstance(x, int) for x in args)):
                self._initialize_from_tuple_ints(args)

        elif len(args) == 2 and all(isinstance(x, int) for x in args):
            self._initialize_from_row_col_idx(*args)

    def _initialize_from_tuple_ints(self, tuple_idx: Tuple[int, int]):
        self.row_idx, self.col_idx = tuple_idx
        self._a1_cell = gsh.idx_to_cell(self.row_idx, self.col_idx)

    def _initialize_from_row_col_idx(self, row_col_idx):
        self.row_idx, self.col_idx = row_col_idx
        self._a1_cell = gsh.idx_to_cell(*row_col_idx)

    def _initialize_from_cell(self, a1cell: 'A1Cell'):
        self._a1_cell = a1cell._a1_cell
        self.row_idx, self.col_idx = gsh.cell_to_idx(str(a1cell))

    def __getitem__(self, key):
        if 0 > key > 1:
            raise IndexError(f'Expected 0 or 1: {key}')
        else:
            return self._a1_cell[key]

    def __add__(self, other):
        if isinstance(other, int):
            return

    def __str__(self):
        return self._a1_cell
