from typing import List

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import urllib.parse
import requests

from sbankenssheets.sbanken.transaction import Transaction


class Sbanken(object):

    @staticmethod
    def _create_authenticated_http_session(client_id: str, client_secret: str) -> requests.Session:
        oauth2_client = BackendApplicationClient(client_id=client_id)
        session = OAuth2Session(client=oauth2_client)
        session.fetch_token(
            token_url='https://api.sbanken.no/identityserver/connect/token',
            client_id=client_id,
            client_secret=urllib.parse.quote(client_secret)
        )
        return session

    def __init__(self, client_id: str, client_secret: str, customer_id: str):
        self.session = Sbanken._create_authenticated_http_session(client_id, client_secret)
        self.customer_id = customer_id

    def get_transactions(self,
                         account_id: str,
                         index: int = 0,
                         length: int = 100,
                         start_date=None,
                         end_date=None
                         ) -> List[Transaction]:

        queries = {
            'index': str(index),
            'length': str(length),
            'startDate': start_date,
            'endDate': end_date
        }

        response = self.session.get(
            f'https://api.sbanken.no/bank/api/v1/Transactions/{account_id}',
            headers={
                'customerId': self.customer_id,
            },
            params=queries
        ).json()

        if response['isError']:
            raise RuntimeError(f'{response["errorType"]} {response["errorMessage"]}')

        transactions = [Transaction(transaction) for transaction in response['items']]

        return transactions

    def get_accounts(self):
        response = self.session.get(
            "https://api.sbanken.no/bank/api/v1/Accounts",
            headers={'customerId': self.customer_id}
        ).json()

        if not response["isError"]:
            return response["items"]
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))
