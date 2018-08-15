from pprint import pprint

from Sbanken import Sbanken
from google_sheets import GSheets
from transaction import divide_transactions


def main():
    import private_api_keys
    import urls

    sbanken = Sbanken(private_api_keys.CLIENTID, private_api_keys.SECRET, private_api_keys.CUSTOMERID)

    accounts = sbanken.get_accounts()
    account = accounts[0]

    transactions = sbanken.get_transactions(account['accountId'],
                                            startDate='2018-08-01',
                                            length=5,
                                            index=5)

    service = GSheets(urls.spreadsheet_id)

    divided_transactions = divide_transactions(transactions)

    # Append expenses
    values = list(map(lambda t: t.to_sheets_row(), divided_transactions['expenses']))
    response = service.append('Dummy!B5:E', list(reversed(values)))

    pprint(response)

    # Append income
    values = list(map(lambda t: t.to_sheets_row(), divided_transactions['income']))
    response = service.append('Dummy!G5:J', list(reversed(values)))

    pprint(response)


def sbanken():
    import private_api_keys

    sbanken = Sbanken(private_api_keys.CLIENTID, private_api_keys.SECRET, private_api_keys.CUSTOMERID)

    accounts = sbanken.get_accounts()

    account = accounts[0]

    transactions = sbanken.get_transactions(account['accountId'],
                                            startDate='2018-08-01',
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

    response = service.append('Dummy!B5:E', values)

    pprint(response)


if __name__ == "__main__":
    # sbanken()
    # sheets()
    main()