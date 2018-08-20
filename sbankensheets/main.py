from pprint import pprint

from sbankensheets.sbanken import Sbanken, Transaction, divide_transactions, filter_transactions
from sbankensheets.gsheets import GSheet, A1Range


def main():
    from sbankensheets import private_api_keys
    from sbankensheets import urls
    from sbankensheets.gsheets import google_sheets_helpers as gs

    sbanken = Sbanken(private_api_keys.CLIENTID, private_api_keys.SECRET, private_api_keys.CUSTOMERID)

    accounts = sbanken.get_accounts()

    # Todo: make this pretty
    for account in accounts:
        if account['name'] == 'Sparekonto':
            savings_account = account['accountId']

    account = accounts[0]

    transactions = sbanken.get_transactions(account['accountId'],
                                            start_date='2018-08-01',
                                            length=1000)

    gsheets = GSheet(urls.spreadsheet_id)

    divided_transactions = divide_transactions(transactions)

    # Todo: Include savings
    # Start cells
    expenses_date_cell, income_date_cell, *savings_date_cell = gs.find_cells(gsheets, 'Dummy', 'Dato')

    for transaction_date_cell, name in zip((expenses_date_cell, income_date_cell),
                                           ('expenses', 'income')):

        # Subtract a column for encoding
        transaction_encoding_cell = transaction_date_cell - (1, 0)

        # Extract encoding
        # + (0, 1) for dropping header
        transaction_encodings_range = A1Range.from_cell(transaction_encoding_cell + (0, 1), sheet='Dummy')

        transaction_enc_values = gsheets.get(transaction_encodings_range)['values']

        gs_transaction = map(lambda x: Transaction.decode(x[0]), filter(lambda x: not (x[0] == '.'),
                                                                        transaction_enc_values))

        filtered_transactions = filter_transactions(divided_transactions[name], gs_transaction)

        transaction_range = A1Range.from_cell(transaction_encoding_cell, range=(4, 0), sheet='Dummy')

        # Append transactions
        values = list(map(lambda t: t.to_sheets_row(encode=True), filtered_transactions))
        # Reverse order to ascending
        values = values[::-1]
        response = gsheets.append(transaction_range, values)

        pprint(response)


if __name__ == "__main__":
    main()
