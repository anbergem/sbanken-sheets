from typing import List, Dict, Tuple, Union

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


class GSheets(object):

    @staticmethod
    def _create_authenticated_google_service():
        SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
        store = file.Storage('auth/token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('auth/credentials.json', SCOPES)
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
    def __init__(self, *args: Union['A1Cell', int, str]):
        self._base_col = ord('A')
        self._last_col = ord('Z')
        if len(args) == 1:
            if isinstance(args[0], A1Cell):
                self._initialize_from_cell(args[0])
            elif isinstance(args[0], str):
                self._initialize_from_str(args[0])
            elif all(isinstance(x, int) for x in args[0]):
                self._initialize_from_col_row_idx(*args[0])
        elif len(args) == 2 and all(isinstance(x, int) for x in args):
            self._initialize_from_col_row_idx(args)
        else:
            raise ValueError(f'{args} is not a valid constructor parameter.')

    def _initialize_from_col_row_idx(self, col_row_idx):
        self._idxs = list(col_row_idx)

    def _initialize_from_cell(self, a1cell: 'A1Cell'):
        self._idxs = list(cell_to_idx(str(a1cell)))

    def _initialize_from_str(self, args):
        self._idxs = list(cell_to_idx(args))

    def __getitem__(self, key) -> str:
        if key < 0 or key > 1:
            raise IndexError(f'Expected 0 or 1: {key}')
        return str(self)[key]

    def __setitem__(self, key: int, value: Union[str, int]):
        if key not in (0, 1):
            raise IndexError(f'Expected key 0 or 1: {key}')
        if key == 1:  # row
            self._idxs[1] = value
        else:  # column
            if isinstance(value, str) \
                    and len(value) == 1 \
                    and (self._base_col <= ord(value.upper()) <= self._last_col):
                self._idxs[0] = ord(value.upper()) - self._base_col
            elif isinstance(value, int) and (25 >= value >= 0):
                self._idxs[0] = value
            else:
                raise ValueError('Columns above Z are not supported.')

    def __add__(self, value: Union[Tuple[int, int], List[int]]):
        if isinstance(value, (tuple, list)) and len(value) == 2 and all(isinstance(x, int) for x in value):
            return A1Cell(self._add_to_col(value[0]), self._idxs[1] + value[1])

        raise ValueError(f'Expected tuple of two ints: {value.__class__}')

    def __str__(self):
        return idx_to_cell(*self._idxs)

    def __eq__(self, other):
        return str(self) == str(other)

    def _add_to_col(self, value):
        if self._idxs[0] + value > 25:
            raise ValueError('Columns above Z are not supported.')
        return self._idxs[0] + value


class A1Range(object):
    def __init__(self, start: A1Cell, end_cell: A1Cell=None, range: Tuple[int, int]=None):
        if not end_cell and not range:
            raise ValueError('Must sepcify end_cell or range')
        elif end_cell and range:
            raise ValueError('Cannot specify both end_cell and range')
        elif end_cell:
            self._range = (start, end_cell)
        elif range:
            self._range = (start, A1Cell(start+range))

    def __str__(self) -> str:
        return '{}:{}'.format(*self._range)

    def __getitem__(self, key: int) -> A1Cell:
        if 0 > key > 1:
            raise IndexError(f'Expected 0 or 1: {key}')
        return self._range[key]


def idx_to_row(idx: int) -> int:
    return idx+1


def idx_to_col(col: int) -> str:
    # Does not support columns above Z
    if col > 25:
        raise ValueError(f'Columns above idx 25 (Z) are not supported')
    return f'{chr(ord("A")+col)}'


def idx_to_cell(col: int, row: int) -> str:
    return f'{idx_to_col(col)}{idx_to_row(row)}'


def cell_to_idx(cell: str) -> Tuple[int, int]:
    import re

    match = re.match(r'(^[A-Z]+)([0-9]+$)', cell)

    if not match:
        raise ValueError(f'Invalid cell: {cell}')

    col, row = match.groups()

    col_idx = col_to_index(col)
    row_idx = row_to_index(int(row))

    return col_idx, row_idx


def row_to_index(row: int) -> int:
    return row - 1


def col_to_index(col: 'str') -> int:
    # Does not suppoert columns above Z
    if len(col) > 1:
        raise ValueError(f'Columns above Z are not supported: {col}')

    return ord(col) - ord('A')


if __name__ == '__main__':
    c1 = A1Cell('C1')

    c1 += (4, 0)
    print(c1)