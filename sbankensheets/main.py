from pprint import pprint

import sbankensheets.sbanken as sb
import sbankensheets.gsheets as gs
import sbankensheets.categorize as ct
from sbankensheets.gsheets import urls


def main():
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())

    sbanken = sb.SbankenSession()

    account = sbanken.get_account("Brukskonto")

    transactions = sbanken.get_transactions(
        account["accountId"], start_date="2018-08-12", length=1000
    )

    gsheet = gs.GSheet(urls.spreadsheet_id)

    categories = ct.get_categories(gsheet)

    sheet = "Dummy"

    divided_transactions = sb.divide_transactions(
        transactions,
        (
            ("expenses", lambda x: x.amount < 0 and x.transaction_type_code != 200),
            ("income", lambda x: x.amount > 0 and x.transaction_type_code != 200),
            ("savings", lambda x: x.amount < 0 and x.transaction_type_code == 200),
        ),
    )

    # Start cells
    expenses_date_cell, income_date_cell, savings_date_cell = gs.find_cells(
        gsheet, sheet, "Dato"
    )

    for transaction_date_cell, name in zip(
        (expenses_date_cell, income_date_cell, savings_date_cell),
        ("expenses", "income", "savings"),
    ):
        for transaction in divided_transactions[name]:
            category = ct.categorize(transaction, categories[name])
            transaction.category = category

        # Subtract a column for encoding
        transaction_id_cell = transaction_date_cell - (1, 0)

        # Extract encoding
        # + (0, 1) for dropping header
        transaction_id_range = gs.A1Range.from_cell(
            transaction_id_cell + (0, 1), sheet=sheet
        )

        transaction_ids = gsheet.get(transaction_id_range)
        transaction_id_values = transaction_ids["values"]

        # If transactions are manually entered, they're id should me '.'
        gs_automatic_cell_values = gs.filter_manual_cell_values(transaction_id_values)
        gs_transactions = sb.cell_values_to_transactions(gs_automatic_cell_values)

        sb_transactions = divided_transactions[name]
        filtered_transactions = sb.filter_transactions(sb_transactions, gs_transactions)

        transaction_range = gs.A1Range.from_cell(
            transaction_id_cell, range=(4, 0), sheet=sheet
        )

        # Append transactions
        values = list(
            map(lambda t: t.to_sheets_row(encode=True), filtered_transactions)
        )
        # Reverse order to ascending
        values = values[::-1]
        response = gsheet.append(transaction_range, values)

        pprint(response)


if __name__ == "__main__":
    main()
