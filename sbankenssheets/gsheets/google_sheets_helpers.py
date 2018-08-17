from typing import List, Optional, Tuple

from sbankenssheets.gsheets.google_sheets import GSheets, idx_to_cell


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





if __name__ == '__main__':
    print(cell_to_idx('A8865'))
