from pprint import pprint

from Sbanken import Sbanken


def main():
    import private_api_keys

    sbanken = Sbanken(private_api_keys.CLIENTID, private_api_keys.SECRET, private_api_keys.CUSTOMERID)

    transactions = sbanken.get_transactions('6F0CBEE700A52FDA316D02BEECAAFBCC', startDate='2018-08-01')

    filtered = filter(lambda x: x.category, transactions)
    for t in filtered:
        print(f'text: {t.text}, amount: {t.amount}, category: {t.category}')
    # pprint(list(filter(lambda x: x['transactionTypeText'], map(lambda x: x.data, transactions))))


if __name__ == "__main__":
    main()