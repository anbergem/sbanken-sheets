from typing import List, Optional

from sbankensheets.gsheets.google_sheets import GSheet
from sbankensheets.gsheets.a1 import A1Cell, A1Range


def find_cells(gsheet: GSheet, sheet: str, value: str) -> Optional[List[A1Cell]]:
    """
    Find cells with value in a GSheet.

    :param gsheet: The GSheet spreadsheet to find the cells
    :param sheet: The sheet within the GSheet spreadsheet
    :param value: The cell value to be found
    :return: If value is found, a list of A1Cells, else None
    """
    response = gsheet.get(A1Range(sheet=sheet))

    values = response.get('values', [])

    if not values:
        return None

    # Find the position of cells with Dato
    for i, row in enumerate(values):
        if value in row:
            return [A1Cell(j, i) for j, cell in enumerate(row) if cell == value]

    return None


def find_transaction_range(start_cell: str, encoding: bool=True) -> str:
    start_col = start_cell[0]
    end_col = chr(ord(start_col) + 4 if encoding else 3)
    return f'{start_cell}:{end_col}'
