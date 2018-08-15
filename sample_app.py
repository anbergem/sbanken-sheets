import requests


def enable_debug_logging():
    import logging

    import http.client
    http.client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def get_customer_information(http_session: requests.Session, customerid):
    response_object = http_session.get(
        "https://api.sbanken.no/customers/api/v1/Customers",
        headers={'customerId': customerid}
    )
    print(response_object)
    print(response_object.text)
    response = response_object.json()

    if not response["isError"]:
        return response["item"]
    else:
        raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


def get_accounts(http_session: requests.Session, customerid):
    response = http_session.get(
        "https://api.sbanken.no/bank/api/v1/Accounts",
        headers={'customerId': customerid}
    ).json()

    if not response["isError"]:
        return response["items"]
    else:
        raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


def get_transactions(http_session: requests.Session, customerid):
    response = http_session.get(
        f"https://api.sbanken.no/bank/api/v1/Transactions/6F0CBEE700A52FDA316D02BEECAAFBCC",
        headers={
            'customerId': customerid,
            'startDate': '2018-08-01'
        }
    ).json()

    if not response["isError"]:
        return response["items"]
    else:
        raise RuntimeError(f"{response['errorType']} {response['errorMessage']}")


def main():
    # enable_debug_logging()
    import private_api_keys
    import pprint

    from sbanken_session import create_authenticated_http_session

    http_session = create_authenticated_http_session(private_api_keys.CLIENTID, private_api_keys.SECRET)

    # customer_info = get_customer_information(http_session, private_api_keys.CUSTOMERID)
    # pprint.pprint(customer_info)
    #
    # accounts = get_accounts(http_session, private_api_keys.CUSTOMERID)
    # pprint.pprint(accounts)

    transactions = get_transactions(http_session, private_api_keys.CUSTOMERID)
    pprint.pprint(transactions)


if __name__ == "__main__":
    main()
