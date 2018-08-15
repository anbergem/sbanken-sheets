from pprint import pprint

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from Sbanken import Sbanken
from google_sheets import GSheets


def sbanken():
    import private_api_keys

    sbanken = Sbanken(private_api_keys.CLIENTID, private_api_keys.SECRET, private_api_keys.CUSTOMERID)

    accounts = sbanken.get_accounts()

    account = accounts[0]

    transactions = sbanken.get_transactions(account['accountId'], startDate='2018-08-01', length=5, index=5)

    # filtered = filter(lambda x: x.category, transactions)
    # for t in filtered:
    #     print(f'text: {t.text}, amount: {t.amount}, category: {t.category}')
    # pprint(list(filter(lambda x: x['transactionTypeText'], map(lambda x: x._data, transactions))))
    with open('transactions.txt', 'w') as file:
        for t in transactions:
            file.write(f'{t.to_csv()}\n')


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
    #sbanken()
    sheets()