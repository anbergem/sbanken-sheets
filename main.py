from pprint import pprint

from sbanken import Sbanken
from google_sheets import GSheets
from transaction import divide_transactions


def main():
    import private_api_keys
    import urls
    import google_sheets_helpers as gsh

    sbanken = Sbanken(private_api_keys.CLIENTID, private_api_keys.SECRET, private_api_keys.CUSTOMERID)

    accounts = sbanken.get_accounts()

    # Todo: make this pretty
    for account in accounts:
        if account['name'] == 'Sparekonto':
            savings_account = account['accountId']

    account = accounts[0]

    transactions = sbanken.get_transactions(account['accountId'],
                                            start_date='2018-08-01',
                                            length=5,
                                            index=5)

    service = GSheets(urls.spreadsheet_id)

    divided_transactions = divide_transactions(transactions)

    # Todo: Include savings
    # Start cells
    expenses, income, *savings = gsh.find_date_cells(service, 'Dummy')

    expenses_range = gsh.find_transaction_range(expenses)
    income_range = gsh.find_transaction_range(income)

    # Append expenses
    values = list(map(lambda t: t.to_sheets_row(), divided_transactions['expenses']))
    response = service.append(f'Dummy!{expenses_range}', list(reversed(values)))

    pprint(response)

    # Append income
    values = list(map(lambda t: t.to_sheets_row(), divided_transactions['income']))
    response = service.append(f'Dummy!{income_range}', list(reversed(values)))

    pprint(response)


def sbanken():
    import private_api_keys

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
    pprint([x._data for x in transactions])
    # with open('transactions.txt', 'w') as file:
    #     for t in transactions:
    #         file.write(f'{t.to_csv()}\n')


def sheets():
    import urls
    service = GSheets(urls.spreadsheet_id)

    values = [
        ['En dato', '55', 'beskrivelse', 'Kategori?'],
        ['12/10/2018', '129', 'Netflix', 'TV-abonnoment']
    ]

    # response = service.append('Dummy!B5:E', values)

    import google_sheets_helpers as gsh

    expenses, income, savings, *_ = gsh.find_date_cells(service, 'Dummy')

    print(expenses, income, savings)


if __name__ == "__main__":
    sbanken()
    # sheets()
    # main()
