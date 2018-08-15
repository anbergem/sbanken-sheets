from typing import Optional


class Transaction(object):

    def __init__(self, data):
        self._data = data
        self.category = self.categorize();

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return str(self._data)

    @property
    def amount(self):
        return self._data['amount']

    @property
    def text(self) -> str:
        return self._data['text']

    @text.setter
    def text(self, new_text: str):
        self._data['new_text'] = new_text

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value: str):
        self._category = value

    def categorize(self) -> Optional[str]:
        from constants import transaction_keywords

        for keyword in transaction_keywords:
            if keyword['description'].lower() in self.text.lower():
                return keyword['category']

        return None
