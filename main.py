from pprint import pprint

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from Sbanken import Sbanken


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
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    import urls
    # Call the Sheets API
    SPREADSHEET_ID = urls.spreadsheet_id
    # RANGE_NAME = ['Dummy!B5:E', 'Dummy!G5:J', 'Dummy!L5:O']
    RANGE_NAME = 'Dummy!B5:E'
    # result = service.spreadsheets().values().batchGet(spreadsheetId=SPREADSHEET_ID,
    #                                                   ranges=RANGE_NAME).execute()
    #
    # for value_range in result['valueRanges']:
    #     pprint(value_range)
    #     values = value_range.get('values', [])
    #
    #     if not values:
    #         print('No data found.')
    #     else:
    #         for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                # print(','.join(row))

    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body={
            'range': RANGE_NAME,
            'values': [
                ['En dato', '55', 'beskrivelse', 'Kategori?'],
                ['12/10/2018', '129', 'Netflix', 'TV-abonnoment']
            ]
        }
    ).execute()

    pprint(result)


if __name__ == "__main__":
    #sbanken()
    sheets()