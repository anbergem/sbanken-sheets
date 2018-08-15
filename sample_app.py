from oauthlib.oauth2 import BackendApplicationClient
import requests
from requests_oauthlib import OAuth2Session
import urllib.parse


def enable_debug_logging():
    import logging

    import http.client
    http.client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def create_authenticated_http_session(client_id, client_secret) -> requests.Session:
    oauth2_client = BackendApplicationClient(client_id=client_id)
    session = OAuth2Session(client=oauth2_client)
    session.fetch_token(
        token_url='https://api.sbanken.no/identityserver/connect/token',
        client_id=client_id,
        client_secret=urllib.parse.quote(client_secret)
    )
    return session


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


def main():
    # enable_debug_logging()
    import private_api_keys
    import pprint

    http_session = create_authenticated_http_session(private_api_keys.CLIENTID, private_api_keys.SECRET)

    customer_info = get_customer_information(http_session, private_api_keys.CUSTOMERID)
    pprint.pprint(customer_info)

    accounts = get_accounts(http_session, private_api_keys.CUSTOMERID)
    pprint.pprint(accounts)


if __name__ == "__main__":
    main()
