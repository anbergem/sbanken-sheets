from typing import List, Dict

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import urllib.parse
import requests

from sbankensheets.sbanken.transaction import Transaction


class Sbanken(object):
    """
    Class for handling HTTPS requests to the REST API from SBanken.
    """

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
        """
        Get the transactions from the given account id
        :param account_id: The account id to retrieve transactions from
        :param index: The start index of the transactions.
        :param length: The maximum number of transactions to return
        :param start_date: The start date of the transactions. Defaults to 30 days before end date.
        :param end_date: The end date of the transactions. Defaults to today's date.
        :return: A list of Transaction objects.
        """
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

    def get_accounts(self) -> List[Dict]:
        """
        Retrieve account information of all accounts for Sbanken object.
        :return: A list of dictionaries, each representing one account.
        """
        response = self.session.get(
            "https://api.sbanken.no/bank/api/v1/Accounts",
            headers={'customerId': self.customer_id}
        ).json()

        if not response["isError"]:
            return response["items"]
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))
