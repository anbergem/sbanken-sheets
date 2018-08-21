import unittest
import unittest.mock as mock

from sbankensheets.sbanken.transaction import Transaction


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
        expected = [trans.encode(), trans.extract_date(), amount, trans.text, ""]
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
        self.transaction.encode()
        mock_base64.urlsafe_b64encode.assert_called_once_with(mock_pickle.dumps())

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    @mock.patch("sbankensheets.sbanken.transaction.pickle")
    def test_encode_return_urlsafe_b64encode_decode(self, mock_pickle, mock_base64):
        string = self.transaction.encode()

        self.assertEqual(string, mock_base64.urlsafe_b64encode().decode())

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    def test_encode_base64_urlsafe_b64encode_decode_called_with_utf8(self, mock_base64):
        self.transaction.encode()
        mock_base64.urlsafe_b64encode().decode.called_once_with("utf-8")

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    @mock.patch("sbankensheets.sbanken.transaction.pickle")
    def test_decode_calls_encode_utf8_on_arg(self, mock_pickle, mock_base64):
        mock_string = mock.Mock()
        Transaction.decode(mock_string)
        mock_string.encode.assert_called_once_with("utf-8")

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    @mock.patch("sbankensheets.sbanken.transaction.pickle")
    def test_decode_base64_urlsafe_64decode_called_with_encoded_arg(
        self, mock_pickle, mock_base64
    ):
        mock_string = mock.Mock()
        Transaction.decode(mock_string)
        mock_base64.urlsafe_b64decode.assert_called_with(mock_string.encode())

    @mock.patch("sbankensheets.sbanken.transaction.base64")
    @mock.patch("sbankensheets.sbanken.transaction.pickle")
    def test_decode_transaction_data_is_decoded(self, mock_pickle, mock_base64):
        mock_string = mock.Mock()
        transaction = Transaction.decode(mock_string)
        self.assertEqual(transaction._data, mock_pickle.loads())
