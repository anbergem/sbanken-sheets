from pprint import pprint

from Sbanken import Sbanken


def main():
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


if __name__ == "__main__":
    main()
