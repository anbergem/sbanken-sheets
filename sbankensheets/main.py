from pprint import pprint

import sbankensheets.sbanken as sb
import sbankensheets.gsheets as gs


def main():
    from sbankensheets import private_api_keys
    from sbankensheets import urls

    sbanken = sb.Sbanken(
        private_api_keys.CLIENTID, private_api_keys.SECRET, private_api_keys.CUSTOMERID
    )

    account = sbanken.get_account("Brukskonto")

    transactions = sbanken.get_transactions(
        account["accountId"], start_date="2018-08-01", length=1000
    )

    gsheets = gs.GSheet(urls.spreadsheet_id)

    divided_transactions = sb.divide_transactions(
        transactions,
        (
            ("expenses", lambda x: x.amount < 0 and x.transaction_type != "Overføring"),
            ("income", lambda x: x.amount > 0 and x.transaction_type != "Overføring"),
            ("savings", lambda x: x.amount < 0 and x.transaction_type == "Overføring"),
        ),
    )

    # Todo: Include savings
    # Start cells
    expenses_date_cell, income_date_cell, savings_date_cell = gs.find_cells(
        gsheets, "Dummy", "Dato"
    )

    for transaction_date_cell, name in zip(
        (expenses_date_cell, income_date_cell, savings_date_cell),
        ("expenses", "income", "savings"),
    ):

        # Subtract a column for encoding
        transaction_encoding_cell = transaction_date_cell - (1, 0)

        # Extract encoding
        # + (0, 1) for dropping header
        transaction_encodings_range = gs.A1Range.from_cell(
            transaction_encoding_cell + (0, 1), sheet="Dummy"
        )

        transaction_enc_values = gsheets.get(transaction_encodings_range)["values"]

        gs_automatic_cell_values = gs.filter_manual_cell_values(transaction_enc_values)
        gs_transaction = sb.cell_values_to_transactions(gs_automatic_cell_values)

        filtered_transactions = sb.filter_transactions(
            divided_transactions[name], gs_transaction
        )

        transaction_range = gs.A1Range.from_cell(
            transaction_encoding_cell, range=(4, 0), sheet="Dummy"
        )

        # Append transactions
        values = list(
            map(lambda t: t.to_sheets_row(encode=True), filtered_transactions)
        )
        # Reverse order to ascending
        values = values[::-1]
        response = gsheets.append(transaction_range, values)

        pprint(response)


if __name__ == "__main__":
    main()
