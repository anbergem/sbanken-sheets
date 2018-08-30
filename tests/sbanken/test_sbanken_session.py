import unittest
import unittest.mock as mock

from sbankensheets.sbanken import SbankenSession, SbankenError


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
        self.sbanken.session.get().json.return_value = {"items": [], "isError": False}
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
        items = [mock.MagicMock(dict), mock.MagicMock(dict), mock.MagicMock(dict)]
        expected = [self.Transaction(item) for item in items]

        self.sbanken.session.get().json.return_value = {
            "items": items,
            "isError": False,
        }

        account_id = "test-account-id"
        response = self.sbanken.get_transactions(account_id=account_id)

        for resp, expc in zip(response, expected):
            self.assertEqual(resp, expc)

    def test_get_transaction_response_is_error_raise_sbanken_error(self):
        self.sbanken.session.get().json.return_value = {
            "isError": True,
            "errorType": None,
            "errorMessage": None,
        }

        account_id = "test-account-id"
        self.assertRaises(SbankenError, self.sbanken.get_transactions, account_id)

    def test_get_accounts_calls_get_with_correct_args(self):
        self.sbanken.session.get().json.return_value = {"items": [], "isError": False}
        # Reset number of times called
        self.sbanken.session.get.reset_mock()

        self.sbanken.get_accounts()

        self.sbanken.session.get.assert_called_once_with(
            f"https://api.sbanken.no/bank/api/v1/Accounts",
            headers={"customerId": self.sbanken.customer_id},
        )

    def test_get_accounts_returns_correct_accounts(self):
        items = [1, 2, 3]
        expected = items

        self.sbanken.session.get().json.return_value = {
            "items": items,
            "isError": False,
        }

        response = self.sbanken.get_accounts()

        for resp, expc in zip(response, expected):
            self.assertEqual(expc, resp)

    def test_get_accounts_returns_is_error_raise_sbanken_error(self):
        self.sbanken.session.get().json.return_value = {
            "isError": True,
            "errorType": None,
            "errorMessage": None,
        }

        self.assertRaises(SbankenError, self.sbanken.get_accounts)

    def test_get_account_with_account_name_calls_get_with_correct_args(self):
        self.sbanken.session.get().json.return_value = {"items": [], "isError": False}
        # Reset number of times called
        self.sbanken.session.get.reset_mock()

        account_name = "test-account-name"
        self.sbanken.get_account(account_name=account_name)

        self.sbanken.session.get.assert_called_once_with(
            f"https://api.sbanken.no/bank/api/v1/Accounts",
            headers={"customerId": self.sbanken.customer_id},
        )

    def test_get_account_with_account_name_returns_correct_account(self):
        correct_name = "correct-name"
        correct_customer_id = self.sbanken.customer_id
        items = [
            {"name": correct_name, "ownerCustomerId": "wrong-customer-id"},
            {"name": correct_name, "ownerCustomerId": correct_customer_id},
            {"name": "wrong-name-2", "ownerCustomerId": correct_customer_id},
        ]
        expected = items[1]
        self.sbanken.session.get().json.return_value = {
            "items": items,
            "isError": False,
        }
        # Reset number of times called
        self.sbanken.session.get.reset_mock()

        actual = self.sbanken.get_account(account_name=correct_name)

        self.assertEqual(expected, actual)

    def test_get_account_with_account_name_customer_id_returns_correct_account(self):
        correct_name = "correct-name"
        correct_customer_id = "test-customer-id"
        items = [
            {"name": correct_name, "ownerCustomerId": "wrong-customer-id"},
            {"name": correct_name, "ownerCustomerId": correct_customer_id},
            {"name": "wrong-name-2", "ownerCustomerId": correct_customer_id},
        ]
        expected = items[1]
        self.sbanken.session.get().json.return_value = {
            "items": items,
            "isError": False,
        }
        # Reset number of times called
        self.sbanken.session.get.reset_mock()

        actual = self.sbanken.get_account(
            account_name=correct_name, customer_id=correct_customer_id
        )

        self.assertEqual(expected, actual)

    def test_get_account_no_items_returns_none(self):
        correct_name = "correct-name"
        items = []
        self.sbanken.session.get().json.return_value = {
            "items": items,
            "isError": False,
        }

        response = self.sbanken.get_account(account_name=correct_name)

        self.assertIsNone(response)

    def test_get_account_response_is_error_raise_sbanken_error(self):
        self.sbanken.session.get().json.return_value = {
            "isError": True,
            "errorType": None,
            "errorMessage": None,
        }

        account_name = "test-account-name"
        self.assertRaises(SbankenError, self.sbanken.get_account, account_name)

    @mock.patch(
        "sbankensheets.sbanken.sbanken_session.SbankenSession.unstable_transaction_keys"
    )
    def test_transaction_in_unstable_transaction_keys_calls_del_on_keyword_in_transaction(
        self, mock_keys
    ):
        transaction_mock = mock.MagicMock()
        transaction_mock.__contains__.return_value = True

        test_keyword = "test-keyword"
        mock_keys.__iter__.return_value = [test_keyword]

        self.sbanken._remove_unstable_transaction_keys([transaction_mock])

        transaction_mock.__delitem__.assert_called_once_with(test_keyword)

    @mock.patch(
        "sbankensheets.sbanken.sbanken_session.SbankenSession.unbooked_text_keywords"
    )
    def test_remove_unbooked_transactions_removes_transactions_with_test_in_keywords(
        self, mock_keys
    ):
        good_trans_mock = mock.MagicMock()
        good_trans_mock.text.lower().__ne__.return_value = True

        bad_trans_mock = mock.MagicMock()
        bad_trans_mock.text.lower().__ne__.return_value = False

        test_keyword = "test-keyword"
        mock_keys.__iter__.return_value = [test_keyword]

        expected = [good_trans_mock]
        actual = self.sbanken._remove_unbooked_transactions(
            [good_trans_mock, bad_trans_mock]
        )

        self.assertEqual(expected, actual)
