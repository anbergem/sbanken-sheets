from typing import List, Optional, Tuple

from sbankenssheets.gsheets import GSheets


def find_date_cells(service: GSheets, sheet: str, encoding: bool=False) -> Optional[List[str]]:
    response = service.get(sheet)

    values = response.get('values', [])

    if not values:
        return None

    # Find the position of cells with Dato
    for i, row in enumerate(values):
        if 'Dato' in row:
            return [idx_to_cell(i, j-1 if encoding else j) for j, x in enumerate(row) if x == 'Dato']

    return None


def find_transaction_range(start_cell: str, encoding: bool=True) -> str:
    start_col = start_cell[0]
    end_col = chr(ord(start_col) + 4 if encoding else 3)
    return f'{start_cell}:{end_col}'


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
    print(cell_to_idx('A8865'))