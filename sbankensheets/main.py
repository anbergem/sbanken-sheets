from pprint import pprint

from sbankensheets.sbanken import Sbanken, Transaction, divide_transactions
from sbankensheets.gsheets.google_sheets import GSheet, A1Range


def main():
    from sbankensheets import private_api_keys
    from sbankensheets import urls
    from sbankensheets.gsheets import google_sheets_helpers as gsh

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
    expenses, income, *savings = gsh.find_cells(gsheets, 'Dummy', 'Dato')

    # Subtract a column for encoding
    expenses -= (1, 0)
    income -= (1, 0)

    expenses_range = A1Range(expenses, range=(4, 0))
    income_range = A1Range(income, range=(4, 0))

    # Append expenses
    values = list(map(lambda t: t.to_sheets_row(encode=True), divided_transactions['expenses']))
    response = gsheets.append(f'Dummy!{expenses_range}', list(reversed(values)))

    pprint(response)

    # Append income
    values = list(map(lambda t: t.to_sheets_row(encode=True), divided_transactions['income']))
    response = gsheets.append(f'Dummy!{income_range}', list(reversed(values)))

    pprint(response)


def sbanken():
    from sbankensheets import private_api_keys

    sbanken = Sbanken(private_api_keys.CLIENTID, private_api_keys.SECRET, private_api_keys.CUSTOMERID)

    accounts = sbanken.get_accounts()

    account = accounts[0]

    transactions = sbanken.get_transactions(account['accountId'],
                                            start_date='2018-08-01',
                                            length=5,
                                            index=5)

    # filtered = filter(lambda x: x.category, transactions)
    # for t in filtered:
    #     print(f'text: {t.text}, amount: {t.amount}, category: {t.category}')
    encoded = [x.encode() for x in transactions]
    pprint([Transaction.decode(x) for x in encoded])
    # with open('transactions.txt', 'w') as file:
    #     for t in transactions:
    #         file.write(f'{t.to_csv()}\n')


def sheets():
    from sbankensheets import urls
    service = GSheet(urls.spreadsheet_id)

    values = [
        ['En dato', '55', 'beskrivelse', 'Kategori?'],
        ['12/10/2018', '129', 'Netflix', 'TV-abonnoment']
    ]

    # response = service.append('Dummy!B5:E', values)

    from sbankensheets.gsheets import google_sheets_helpers as gsh

    expenses, income, savings, *_ = gsh.find_cells(service, 'Dummy')

    print(expenses, income, savings)


if __name__ == "__main__":
    # sbanken()
    # sheets()
    main()
