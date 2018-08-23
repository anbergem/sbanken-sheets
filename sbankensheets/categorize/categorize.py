from typing import List, Dict, Optional

from sbankensheets.gsheets import GSheet, A1Range
from sbankensheets.gsheets import find_cells
from sbankensheets.sbanken import Transaction

category_sheet = "Kategorier"


def process_category_values(values: List):
    length = len(values)
    category = values[0]
    amount = values[1] if length > 1 else ""
    amount_action = values[2] if length > 2 else ""
    keywords = values[3].split(",") if length > 3 else []

    return {
        "category": category,
        "amount": amount,
        "amount_action": amount_action,
        "keywords": [word.strip().lower() for word in keywords],
    }


def get_categories(gsheet: GSheet):
    cells = find_cells(gsheet, category_sheet, "Kategori")
    if not cells:
        print("No cells found")
        return

    expenses, incomes, savings = cells

    if not expenses or not incomes:
        print(cells)

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


def _categorize_uncertainty(transaction: Transaction, category: Dict):
    amount = transaction.amount if transaction.amount > 0 else -transaction.amount
    if not category["amount_action"] and amount == category["amount"]:
        return True
    elif category["amount_action"] == "+" and amount >= category["amount"]:
        return True
    elif category["amount_action"] == "-" and amount <= category["amount"]:
        return True
    else:
        return False


def categorize(transaction: Transaction, categories) -> Optional[str]:
    print(categories)
    for category in categories:
        keywords = category["keywords"]
        for keyword in keywords:
            if (
                keyword[-1] == "?"
                and keyword[:-1] in transaction.text.lower()
                and _categorize_uncertainty(transaction, category)
            ):
                return category["category"]
            elif keyword in transaction.text.lower():
                return category["category"]
    return None
