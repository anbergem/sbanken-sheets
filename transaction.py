from typing import Optional, Union

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
    def amount(self):
        return self._data['amount']

    @property
    def transaction_type(self):
        return self._data['transactionType']

    @property
    def text(self) -> str:
        return self._data['text']

    @property
    def category(self):
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

    def to_csv(self):
        return ','.join([self.text, str(self.amount), self.category.value if self.category else ''])
