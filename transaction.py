from typing import Optional, Union, List, Dict

from constants import Category


class Transaction(object):

    def __init__(self, data):
        self._data = data
        self.category = self.categorize()

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return str(self._data)

    @property
    def amount(self) -> float:
        return self._data['amount']

    @property
    def transaction_type(self):
        return self._data['transactionType']

    @property
    def text(self) -> str:
        return self._data['text']

    @property
    def category(self) -> Optional[Category]:
        return self._category

    @category.setter
    def category(self, value: Union[str, Category]):
        self._category = value

    def categorize(self) -> Optional[str]:
        from constants import transaction_keywords

        for keyword in transaction_keywords:
            if 'transaction_type' in keyword and keyword['transaction_type'].lower() == self.transaction_type.lower():
                return keyword['category']
            elif keyword['description'].lower() in self.text.lower():
                return keyword['category']

        return None

    def to_csv(self) -> str:
        return ','.join([self.text, str(self.amount), self.category.value if self.category else ''])

    def to_sheets_row(self) -> List[str]:
        return [self.extract_date(), str(self.amount), self.text, self.category.value if self.category else '']

    def extract_date(self) -> str:
        import dateutil.parser as dp

        data = self._data

        if data['cardDetailsSpecified']:
            time = dp.parse(data['cardDetails']['purchaseDate'])
        else:
            time = dp.parse(data['accountingDate'])

        return time.date().isoformat()


def divide_transactions(transactions: List[Transaction], savingsAccount=None) -> Dict[str, List[Transaction]]:
    result = {}

    for transaction in transactions:
        # Todo: Find out how to filter savings transactions
        if transaction._data is None:
            result.get('savings', []).append(transaction)
        elif transaction.amount < 0:
            result.get('expenses', []).append(transaction)
        elif transaction.amount > 0:
            result.get('income', []).append(transaction)

    return result
