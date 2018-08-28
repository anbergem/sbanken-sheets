import unittest
import unittest.mock as mock

from sbankensheets.sbanken.transaction import (
    Transaction,
    divide_transactions,
    filter_transactions,
    cell_values_to_transactions,
)


class TestTransaction(unittest.TestCase):
    def setUp(self):
        super().setUp()
        mock.patch("dateutil.parser")
        self.data = {
            "cardDetailsSpecified": False,
            "transactionType": "Vipps straksbet.",
            "amount": -20.0,
            "transactionTypeText": "",
            "accountingDate": "2018-08-21T00:00:00+02:00",
            "isReservation": True,
            "interestDate": "2018-08-21T00:00:00+02:00",
            "otherAccountNumberSpecified": False,
            "text": "Straksoverføring",
            "transactionTypeCode": 962,
        }

        self.data_with_card_details = {
            "cardDetailsSpecified": True,
            "transactionType": "VISA VARE",
            "amount": -109.0,
            "cardDetails": {
                "merchantName": "Spotify P0701F7525",
                "merchantCity": "Stockholm",
                "transactionId": "4882228048210140",
                "merchantCategoryCode": "5815",
                "originalCurrencyCode": "NOK",
                "merchantCategoryDescription": "Digitale tjenester",
                "currencyAmount": 109.0,
                "currencyRate": 1.0,
                "cardNumber": "*0054",
                "purchaseDate": "2018-08-11T00:00:00+02:00",
            },
            "transactionTypeText": "VISA VARE",
            "accountingDate": "2018-08-14T00:00:00+02:00",
            "isReservation": False,
            "interestDate": "2018-08-14T00:00:00+02:00",
            "otherAccountNumberSpecified": False,
            "text": "*0054 11.08 NOK 109.00 Spotify P0701F7525 Kurs: 1.0000",
            "transactionTypeCode": 714,
        }

        self.transaction = Transaction(self.data)
        self.transaction_with_card_details = Transaction(self.data_with_card_details)

    def tearDown(self):
        super().tearDown()
        mock.patch.stopall()

    def test_to_sheets_row_no_encoding(self):
        trans = self.transaction
        amount = str(-trans.amount).replace(".", ",")
        expected = [trans.extract_date(), amount, trans.text, ""]
        actual = self.transaction.to_sheets_row()

        self.assertEqual(actual, expected)

    def test_to_sheets_row_with_encoding(self):
        trans = self.transaction
        amount = str(-trans.amount).replace(".", ",")
        expected = [trans._encode(), trans.extract_date(), amount, trans.text, ""]
        actual = self.transaction.to_sheets_row(encode=True)

        self.assertEqual(actual, expected)

    @mock.patch("sbankensheets.sbanken.transaction.dateutil.parser")
    def test_extract_date_no_card_details_calls_parser_with_correct_data(
        self, mock_parser
    ):
        self.transaction.extract_date()
        mock_parser.parse.assert_called_once_with(self.data["accountingDate"])

    @mock.patch("sbankensheets.sbanken.transaction.dateutil.parser")
    def test_extract_date_no_card_details_returns_time_date_isoformat(
        self, mock_parser
    ):
        time = self.transaction.extract_date()
        self.assertEqual(time, mock_parser.parse().date().isoformat())

    @mock.patch("sbankensheets.sbanken.transaction.dateutil.parser")
    def test_extract_date_with_card_details(self, mock_parser):
        self.transaction_with_card_details.extract_date()
        mock_parser.parse.assert_called_once_with(
            self.data_with_card_details["cardDetails"]["purchaseDate"]
        )

    @mock.patch("sbankensheets.sbanken.transaction.dateutil.parser")
    def test_extract_date_with_card_details_returns_time_date_isoformat(
        self, mock_parser
    ):
        time = self.transaction_with_card_details.extract_date()
        self.assertEqual(time, mock_parser.parse().date().isoformat())

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    @mock.patch("sbankensheets.sbanken.transaction.pickle")
    def test_encode_called_with_pickle_dumps_str(self, mock_pickle, mock_base64):
        self.transaction._encode()
        mock_base64.urlsafe_b64encode.assert_called_once_with(mock_pickle.dumps())

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    @mock.patch("sbankensheets.sbanken.transaction.pickle")
    def test_encode_return_urlsafe_b64encode_decode(self, mock_pickle, mock_base64):
        string = self.transaction._encode()

        self.assertEqual(string, mock_base64.urlsafe_b64encode().decode())

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    def test_encode_base64_urlsafe_b64encode_decode_called_with_utf8(self, mock_base64):
        self.transaction._encode()
        mock_base64.urlsafe_b64encode().decode.called_once_with("utf-8")

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    @mock.patch("sbankensheets.sbanken.transaction.pickle")
    def test_decode_calls_encode_utf8_on_arg(self, mock_pickle, mock_base64):
        mock_string = mock.Mock()
        Transaction._decode(mock_string)
        mock_string.encode.assert_called_once_with("utf-8")

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    @mock.patch("sbankensheets.sbanken.transaction.pickle")
    def test_decode_base64_urlsafe_64decode_called_with_encoded_arg(
        self, mock_pickle, mock_base64
    ):
        mock_string = mock.Mock()
        Transaction._decode(mock_string)
        mock_base64.urlsafe_b64decode.assert_called_with(mock_string.encode())

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    @mock.patch("sbankensheets.sbanken.transaction.pickle")
    def test_decode_transaction_data_is_decoded(self, mock_pickle, mock_base64):
        mock_string = mock.Mock()
        transaction = Transaction._decode(mock_string)
        self.assertEqual(transaction._data, mock_pickle.loads())

    def test_divide_transactions_append_category_func_tuple_if_func(self):
        transactions = [mock.MagicMock(spec=Transaction) for _ in range(3)]
        categories = [
            (mock.MagicMock(spec=str), mock.MagicMock(side_effect=[True, False, True]))
            for _ in range(3)
        ]

        # Because of side effect, divide_transactions should skip transactions[1]
        expected = {
            categories[0][0]: transactions[::2],
            categories[1][0]: transactions[::2],
            categories[2][0]: transactions[::2],
        }

        result = divide_transactions(transactions, categories)

        self.assertEqual(expected, result)

    def test_filter_transactions(self):
        same_mocks = [mock.MagicMock() for _ in range(2)]
        only_first_mocks = [mock.MagicMock() for _ in range(3)]
        first = same_mocks + only_first_mocks
        second = same_mocks + [mock.MagicMock() for _ in range(4)]

        results = filter_transactions(first, second)

        self.assertTrue(
            set(results) == set(only_first_mocks)
            and len(results) == len(only_first_mocks)
        )

    @mock.patch("sbankensheets.sbanken.transaction.Transaction")
    def test_cell_values_to_transactions_calls_decode_on_0_index_for_each_cell_value(
        self, mock_transaction
    ):
        mock_cell_values = [mock.MagicMock() for _ in range(3)]

        # Wrap in list to trigger generator
        list(cell_values_to_transactions(mock_cell_values))

        expected = list(map(lambda x: mock.call(x.__getitem__()), mock_cell_values))
        actual = mock_transaction._decode.call_args_list

        self.assertEqual(expected, actual)
