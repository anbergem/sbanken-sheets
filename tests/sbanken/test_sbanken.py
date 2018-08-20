import unittest
import unittest.mock as mock

from sbankenssheets.sbanken import Sbanken


class TestSbanken(unittest.TestCase):

    def setUp(self):
        super().setUp()
        mock.patch('sbankenssheets.sbanken.sbanken.BackendApplicationClient').start()
        mock.patch('sbankenssheets.sbanken.sbanken.OAuth2Session').start()
        mock.patch('urllib.parse').start()
        mock.patch('requests.Session').start()
        self.Transaction = mock.patch('sbankenssheets.sbanken.sbanken.Transaction').start()

        self.sbanken = Sbanken('test-client-id', 'test-secret', 'test-customer-id')

    def tearDown(self):
        super().tearDown()
        mock.patch.stopall()

    def test_get_transaction_calls_session_get_with_correct_args(self):
        self.sbanken.session.get().json = lambda: {'items': [], 'isError': False}
        # Reset number of times called
        self.sbanken.session.get.reset_mock()

        account_id = 'test-account-id'
        index = 5
        length = 60
        start_date = '02.03.2018'
        end_date = '02.05.2018'
        self.sbanken.get_transactions(
            account_id=account_id,
            index=index,
            length=length,
            start_date=start_date,
            end_date=end_date
        )

        self.sbanken.session.get.assert_called_once_with(
            f'https://api.sbanken.no/bank/api/v1/Transactions/{account_id}',
            headers={
                'customerId': self.sbanken.customer_id,
                'index': str(index),
                'length': str(length),
                'start_date': start_date,
                'end_date': end_date
            }
        )

    def test_get_transaction_returns_correct_transactions(self):
        items = [1, 2, 3]
        expected = [self.Transaction(item) for item in items]

        self.sbanken.session.get().json = lambda: {'items': items, 'isError': False}
        # Reset number of times called
        self.sbanken.session.get.reset_mock()

        account_id = 'test-account-id'
        response = self.sbanken.get_transactions(account_id=account_id)

        for resp, expc in zip(response, expected):
            self.assertEqual(resp, expc)
