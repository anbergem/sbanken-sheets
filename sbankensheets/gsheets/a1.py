from typing import Union, Tuple, List


class A1Cell(object):
    """
    Class for representing the google A1 notation. See https://developers.google.com/sheets/api/guides/concepts.

    An A1Cell can be creating in the following ways, all representing the cell C3:

        >>> a = A1Cell('C3')
        >>> b = A1Cell('c3')
        >>> c = A1Cell(2, 2)
        >>> d = A1Cell([2, 2])
        >>> e = A1Cell((2, 2))
        >>> f = A1Cell(a)
    """
    def __init__(self, *args: Union['A1Cell', int, str, Union[Tuple[int, int], List[int]]]):
        self._base_col = ord('A')
        self._last_col = ord('Z')
        if len(args) == 1:
            if isinstance(args[0], A1Cell):
                self._initialize_from_cell(args[0])
            elif isinstance(args[0], str):
                self._initialize_from_str(args[0])
            elif all(isinstance(x, int) for x in args[0]):
                self._initialize_from_col_row_idx(*args)
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
        if key == 1:
            if isinstance(value, int) and value >= 0:  # row
                self._idxs[1] = value
            else:
                raise ValueError(f'Expected int >= 0: {value}')
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

    def __sub__(self, value: Union[Tuple[int, int], List[int]]):
        if isinstance(value, (tuple, list)) and len(value) == 2 and all(isinstance(x, int) for x in value):
            return A1Cell(self._sub_from_col(value[0]), self._sub_from_row(value[1]))

        raise ValueError(f'Expected tuple of two ints: {value.__class__}')

    def __str__(self) -> str:
        return idx_to_cell(*self._idxs)

    def __eq__(self, other) -> bool:
        if not isinstance(other, A1Cell):
            return False
        return str(self) == str(other)

    def _add_to_col(self, value):
        if self._idxs[0] + value > 25:
            raise ValueError('Columns above Z are not supported.')
        return self._idxs[0] + value

    def _sub_from_row(self, value):
        if self._idxs[1] - value < 0:
            raise ValueError('Cannot subtract from row 0')
        return self._idxs[1] - value

    def _sub_from_col(self, value):
        if self._idxs[0] - value < 0:
            raise ValueError('Cannot subtract from column A.')
        return self._idxs[0] - value


class A1Range(object):
    """
    Class for representing the google A1 notation range, using two A1Cells.

    The A1Range can be created in the any of the following ways, each representing the range C3:E6:

        >>> c3 = A1Cell('C3')
        >>> e6 = A1Cell('E6')
        >>> c3e6 = A1Range(c3, e6)
        >>> c3e6 = A1Range(c3, c3 + (2, 3))
        >>> c3e6 = A1Range.from_cell(c3, (2, 3))
        >>> c3e6 = A1Range.from_str('C3:E6')
        >>> c3e6 = A1Range.from_str('C3', 'E6')

    A range covering the remaining columns can be created in the following ways, each representing the range C3:C

        >>> c3 = A1Cell('C3')
        >>> c3c = A1Range(c3)
        >>> c3c = A1Range.from_cell(c3)
    """
    def __init__(self, start_cell: A1Cell, end_cell: A1Cell=None, sheet: str=None):
        self._range = (start_cell, end_cell)
        self._sheet = sheet

    @classmethod
    def from_cell(cls, start_cell: A1Cell, range: Union[Tuple[int, int], List[int]]=None, sheet: str=None):
        if range and (len(range) != 2 or not all(isinstance(x, int) for x in range)):
            raise ValueError('Range must be tuple/list of two ints')
        return cls(start_cell, start_cell + range if range else None, sheet=sheet)

    @classmethod
    def from_str(cls, string: str, end_cell: str=None, sheet: str=None):
        if not end_cell:
            cells = string.split(":")
            if len(cells) != 2:
                raise ValueError('Cell not in format <start_cell>:<end_cell>')
            return cls(A1Cell(cells[0]), A1Cell(cells[1]))
        return cls(A1Cell(string), A1Cell(end_cell), sheet=sheet)

    @property
    def sheet(self):
        return self._sheet

    @sheet.setter
    def sheet(self, sheet):
        self._sheet = sheet

    def __str__(self) -> str:
        return '{}{}:{}'.format(f"'{self._sheet}'!" if self._sheet else '',
                                self._range[0],
                                self._range[1] if self._range[1] else self._range[0][0])

    def __eq__(self, other) -> bool:
        if not isinstance(other, A1Range):
            return False
        else:
            return self._sheet == other._sheet and all(x == y for x, y in zip(self._range, other._range))

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

    match = re.match(r'(^[a-zA-Z])([0-9]+$)', cell)

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

    return ord(col.upper()) - ord('A')