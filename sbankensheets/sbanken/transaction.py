from typing import Optional, Union, List, Dict, Iterable, Tuple, Callable, Any

from sbankensheets.sbanken.constants import Category
import dateutil.parser
import base64
import pickle


class Transaction(object):
    """
    Class representing a transaction obtained by Sbanken.
    """

    def __init__(self, data):
        for keyword in ("transactionId", "source", "reservationType"):
            if keyword in data:
                del data[keyword]
        self._data = data
        self._id = self._encode()
        self.category = self.categorize()

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
    def text(self) -> str:
        return self._data["text"]

    @property
    def category(self) -> Optional[Category]:
        return self._category

    @category.setter
    def category(self, value: Union[str, Category]):
        self._category = value

    @property
    def id(self) -> str:
        return self._id

    def categorize(self) -> Optional[str]:
        from sbankensheets.sbanken.constants import transaction_keywords

        for keyword in transaction_keywords:
            if (
                "transaction_type" in keyword
                and keyword["transaction_type"].lower() == self.transaction_type.lower()
            ):
                return keyword["category"]
            elif keyword["description"].lower() in self.text.lower():
                return keyword["category"]

        return None

    def to_csv(self) -> str:
        return ",".join(
            [self.text, str(self.amount), self.category.value if self.category else ""]
        )

    def to_sheets_row(self, encode: bool = False) -> List[str]:
        result = [self._encode()] if encode else []
        return result + [
            self.extract_date(),
            str(self.amount if self.amount > 0 else -self.amount).replace(".", ","),
            self.text,
            self.category.value if self.category else "",
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
    transactions: List[Transaction], categories
) -> Dict[str, List[Transaction]]:

    result = {}

    for transaction in transactions:
        for category, func in categories:
            if func(transaction):
                result[category] = result.get(category, []) + [transaction]

    return result


def filter_transactions(first: Iterable[Transaction], second: Iterable[Transaction]):
    second_data = list(map(lambda x: x._data, second))
    filtered = list(filter(lambda x: x._data not in second_data, first))
    return filtered


def cell_values_to_transactions(cell_values: Iterable) -> Iterable:
    return map(lambda x: Transaction._decode(x[0]), cell_values)
