import base64
import pickle
from typing import List, Dict, Iterable, Sequence

import dateutil.parser


class Transaction(object):
    """
    Class representing a transaction obtained by Sbanken.
    """

    def __init__(self, data):
        self._data = data
        self._id = self._encode()
        self.category = ""

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return str(self._data)

    @property
    def amount(self) -> float:
        return self._data["amount"]

    @property
    def transaction_type(self):
        return self._data["transactionType"]

    @property
    def transaction_type_code(self) -> int:
        return self._data["transactionTypeCode"]

    @property
    def text(self) -> str:
        return self._data["text"]

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str):
        self._category = value

    @property
    def id(self) -> str:
        return self._id

    def to_csv(self) -> str:
        return ",".join(
            [self.text, str(self.amount), self.category.value if self.category else ""]
        )

    def to_sheets_row(self, encode: bool = False) -> Sequence[str]:
        result = [self._encode()] if encode else []
        return result + [
            self.extract_date(),
            str(self.amount if self.amount > 0 else -self.amount).replace(".", ","),
            self.text,
            self.category,
        ]

    def extract_date(self) -> str:
        data = self._data

        if data["cardDetailsSpecified"]:
            time = dateutil.parser.parse(data["cardDetails"]["purchaseDate"])
        else:
            time = dateutil.parser.parse(data["accountingDate"])

        return time.date().isoformat()

    @staticmethod
    def from_id(id: str) -> "Transaction":
        return Transaction._decode(id)

    @staticmethod
    def _decode(encoded_str: str) -> "Transaction":
        encoded_bytes = encoded_str.encode("utf-8")
        data_str = base64.urlsafe_b64decode(encoded_bytes)
        data = pickle.loads(data_str)

        return Transaction(data)

    def _encode(self) -> str:
        data_str = pickle.dumps(self._data)

        return base64.urlsafe_b64encode(data_str).decode("utf-8")


def divide_transactions(
    transactions: Sequence[Transaction], categories
) -> Dict[str, List[Transaction]]:

    result = {category: [] for category in map(lambda x: x[0], categories)}

    for transaction in transactions:
        for category, func in categories:
            if func(transaction):
                result[category].append(transaction)

    return result


def filter_transactions(first: Iterable[Transaction], second: Iterable[Transaction]):
    second_data = list(map(lambda x: x._data, second))
    filtered = list(filter(lambda x: x._data not in second_data, first))
    return filtered


def cell_values_to_transactions(cell_values: Iterable) -> Iterable:
    return map(lambda x: Transaction._decode(x[0]), cell_values)
