from dataclasses import dataclass, field
from typing import List, Optional

from sbankensheets.gsheets import GSheet, A1Range
from sbankensheets.gsheets import find_cells
from sbankensheets.sbanken import Transaction

category_sheet = "Kategorier"


@dataclass
class Category:
    name: str
    amount: float = None
    amount_action: str = None
    keywords: List[str] = field(default_factory=list)


def process_category_values(values: List):
    length = len(values)
    if length < 1:
        raise ValueError(f"values must be of length > 0: {length}")
    category = values[0]
    # Does amount need to be cast to int/float?
    amount = values[1] if length > 1 and values[1] else None
    amount_action = values[2] if length > 2 and values[2] else None
    keywords = values[3].split(",") if length > 3 and values[3] else []

    return Category(
        category, amount, amount_action, [word.strip().lower() for word in keywords]
    )


def get_categories(gsheet: GSheet):
    cells = find_cells(gsheet, category_sheet, "Kategori")
    if not cells:
        print("No cells found")
        return
    expenses, incomes, savings = cells

    categories = {"expenses": [], "income": [], "savings": []}

    for transaction, category_cell in zip(
        sorted(categories.keys()), (expenses, incomes, savings)
    ):
        end_cell = (category_cell + (3, 0))[0]
        category_range = A1Range(
            category_cell + (0, 2), end_cell=end_cell, sheet=category_sheet
        )
        category_cells = gsheet.get(
            category_range, value_render_option="UNFORMATTED_VALUE"
        )
        if "values" not in category_cells:
            print("Values not in sheet")
            return

        category_values = category_cells["values"]

        # Filter empty categories
        filtered_category_values = list(filter(lambda x: x, category_values))

        for category in filtered_category_values:
            categories[transaction].append(process_category_values(category))

    return categories


def _categorize_uncertainty(transaction: Transaction, category: Category):
    amount = transaction.amount if transaction.amount > 0 else -transaction.amount
    if not category.amount_action and amount == category.amount:
        return True
    elif category.amount_action == "+" and amount >= category.amount:
        return True
    elif category.amount_action == "-" and amount <= category.amount:
        return True
    else:
        return False


def categorize(transaction: Transaction, categories: List[Category]) -> Optional[str]:
    # Used for the * keyword. Search other categories first.
    value = None
    for category in categories:
        keywords = category.keywords
        for keyword in keywords:
            if (
                keyword[-1] == "?"
                and keyword[:-1] in transaction.text.lower()
                and _categorize_uncertainty(transaction, category)
            ):
                return category.name
            elif keyword in transaction.text.lower():
                return category.name
            elif keyword == "*":
                value = category.name
    return value
