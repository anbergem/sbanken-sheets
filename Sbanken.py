from typing import List

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import urllib.parse
import requests

from transaction import Transaction


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
                         startDate = None,
                         endDate = None
                         ) -> List[Transaction]:
        # Gather parameters and stringify them. Exclude values not being sent to headers.
        kwargs = {key: str(value) for key, value in locals().items() if key not in ['self', 'account_id']}

        response = self.session.get(
            f'https://api.sbanken.no/bank/api/v1/Transactions/{account_id}',
            headers={
                'customerId': self.customer_id,
                'startDate': 'Aug 15, 2018 at 2:51 PM',
                'endDate': 'Aug 01, 2018 at 2:51 PM'
            }
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
