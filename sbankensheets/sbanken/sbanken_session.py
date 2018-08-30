import urllib.parse
from os import environ
from typing import List, Dict, Optional, Sequence

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from ..sbanken.errors import SbankenError
from ..sbanken.transaction import Transaction


class SbankenSession(object):
    """
    Class for handling HTTPS requests to the REST API from SBanken.
    """

    @staticmethod
    def _create_authenticated_http_session(
        client_id: str, client_secret: str
    ) -> requests.Session:
        oauth2_client = BackendApplicationClient(client_id=client_id)
        session = OAuth2Session(client=oauth2_client)
        session.fetch_token(
            token_url="https://api.sbanken.no/identityserver/connect/token",
            client_id=client_id,
            client_secret=urllib.parse.quote(client_secret),
        )
        return session

    def __init__(self):
        self.session = SbankenSession._create_authenticated_http_session(
            environ["CLIENT_ID"], environ["CLIENT_SECRET"]
        )
        self.customer_id = environ["CUSTOMER_ID"]

    def get_transactions(
        self,
        account_id: str,
        index: int = 0,
        length: int = 100,
        start_date=None,
        end_date=None,
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
            "index": str(index),
            "length": str(length),
            "startDate": start_date,
            "endDate": end_date,
        }

        response = self.session.get(
            f"https://api.sbanken.no/bank/api/v1/Transactions/{account_id}",
            headers={"customerId": self.customer_id},
            params=queries,
        ).json()

        if response["isError"]:
            raise SbankenError(f'{response["errorType"]} {response["errorMessage"]}')

        transactions = [Transaction(transaction) for transaction in response["items"]]

        return transactions

    def get_accounts(self) -> Sequence[Dict]:
        """
        Retrieve account information of all accounts for Sbanken object.
        :return: A list of dictionaries, each representing one account.
        """
        response = self.session.get(
            "https://api.sbanken.no/bank/api/v1/Accounts",
            headers={"customerId": self.customer_id},
        ).json()

        if not response["isError"]:
            return response["items"]
        else:
            raise SbankenError(f'{response["errorType"]} {response["errorMessage"]}')

    def get_account(self, account_name, customer_id=None) -> Optional[Dict]:
        """
        Retrieve account information for a specific account, id'd by the
        account name and the customer id of the owner.

        :param account_name: Name of the account
        :param customer_id: Customer id of the owner of the account. Defaults to
        the customer id of the Sbanken class.
        :return: The account if found, else None.
        """
        if customer_id is None:
            customer_id = self.customer_id

        response = self.session.get(
            "https://api.sbanken.no/bank/api/v1/Accounts",
            headers={"customerId": self.customer_id},
        ).json()

        if response["isError"]:
            raise SbankenError(f'{response["errorType"]} {response["errorMessage"]}')

        accounts = response["items"]

        for account in accounts:
            if (
                account["name"] == account_name
                and account["ownerCustomerId"] == customer_id
            ):
                return account

        return None
