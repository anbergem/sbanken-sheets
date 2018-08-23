import unittest
import unittest.mock as mock
import os

from sbankensheets.definitions import AUTH_PATH
from sbankensheets.sbanken import SbankenSession


class TestSbanken(unittest.TestCase):
    def setUp(self):
        super().setUp()
        mock.patch(
            "sbankensheets.sbanken.sbanken_session.BackendApplicationClient"
        ).start()
        mock.patch("sbankensheets.sbanken.sbanken_session.OAuth2Session").start()
        mock.patch("sbankensheets.sbanken.sbanken_session.environ").start()
        mock.patch("urllib.parse").start()
        mock.patch("requests.Session").start()
        self.Transaction = mock.patch(
            "sbankensheets.sbanken.sbanken_session.Transaction"
        ).start()

        self.sbanken = SbankenSession()

    def tearDown(self):
        super().tearDown()
        mock.patch.stopall()

    def test_get_transaction_calls_session_get_with_correct_args(self):
        self.sbanken.session.get().json = lambda: {"items": [], "isError": False}
        # Reset number of times called
        self.sbanken.session.get.reset_mock()

        account_id = "test-account-id"
        index = 5
        length = 60
        start_date = "02.03.2018"
        end_date = "02.05.2018"
        self.sbanken.get_transactions(
            account_id=account_id,
            index=index,
            length=length,
            start_date=start_date,
            end_date=end_date,
        )

        self.sbanken.session.get.assert_called_once_with(
            f"https://api.sbanken.no/bank/api/v1/Transactions/{account_id}",
            headers={"customerId": self.sbanken.customer_id},
            params={
                "index": str(index),
                "length": str(length),
                "startDate": start_date,
                "endDate": end_date,
            },
        )

    def test_get_transaction_returns_correct_transactions(self):
        items = [1, 2, 3]
        expected = [self.Transaction(item) for item in items]

        self.sbanken.session.get().json = lambda: {"items": items, "isError": False}
        # Reset number of times called
        self.sbanken.session.get.reset_mock()

        account_id = "test-account-id"
        response = self.sbanken.get_transactions(account_id=account_id)

        for resp, expc in zip(response, expected):
            self.assertEqual(resp, expc)
