"""
    BNI Helper
    _____________________
    this is test case where wallet communicate with BNI VA & COre Banking API
"""
from unittest.mock import Mock, patch

from datetime import datetime

from task.test.base import BaseTestCase
from task.bank.BNI.core.services import CoreBank, ApiError

from task.bank.BNI.core.helper import CallError
from werkzeug.contrib.cache import SimpleCache


class TestMockCoreBank(BaseTestCase):
    """ This is class to test by mocking all response from BNI COre Bank helper"""

    @patch("requests.request")
    def test_post_json_success(self, mock_post):
        """ test function to mock success post json request"""
        payload = {"accountNo": "11547119"}

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getBalanceResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2017-02-24T14:12:25.871Z",
                    "customerName": "Bpk JONOMADE MADEMADEMADEMADE IMAMADE",
                    "accountCurrency": "IDR",
                    "accountBalance": 16732765949981,
                },
            }
        }
        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_value

        response = CoreBank(access_token)._api_call(
            api_name="GET_BALANCE", payload=payload
        )
        self.assertEqual(response["data"], expected_value)

    # end def

    @patch("requests.request")
    def test_get_balance_success(self, mock_post):
        """ test function to get balance from BNI server using mock response"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getBalanceResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2017-02-24T14:12:25.871Z",
                    "customerName": "Bpk JONOMADE MADEMADEMADEMADE IMAMADE",
                    "accountCurrency": "IDR",
                    "accountBalance": 16732765949981,
                },
            }
        }
        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_value

        response = CoreBank(access_token).get_balance({"account_no": "12345"})
        self.assertEqual(
            response["data"]["bank_account_info"]["customer_name"],
            expected_value["getBalanceResponse"]["parameters"]["customerName"],
        )
        self.assertEqual(
            response["data"]["bank_account_info"]["balance"],
            expected_value["getBalanceResponse"]["parameters"]["accountBalance"],
        )

    # end def

    @patch("requests.request")
    def test_get_balance_failed(self, mock_post):
        """ test function that failed to get balance from bni server"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getBalanceResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0000",
                    "errorMessage": "Unknown Output",
                    "responseMessage": "Request failed",
                    "responseTimestamp": "2017-02-24T14:12:25.871Z",
                },
            }
        }
        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBank(access_token).get_balance({"account_no": "12345"})

    # end def

    @patch("requests.request")
    def test_get_inhouse_inquiry_bank_account_success(self, mock_post):
        """ test function to get successful inhouse inquiry"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getInHouseInquiryResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2017-09-07T14:10:23.431Z",
                    "customerName": "Bpk JONOMADE MADEMADEMADEMADE IMAMADE",
                    "accountCurrency": "IDR",
                    "accountNumber": "0115475045",
                    "accountStatus": "BUKA",
                    "accountType": "DEP",
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBank(access_token).get_inhouse_inquiry({"account_no": "12345"})
        self.assertEqual(
            response["data"]["bank_account_info"]["account_no"],
            expected_value["getInHouseInquiryResponse"]["parameters"]["accountNumber"],
        )
        self.assertEqual(
            response["data"]["bank_account_info"]["customer_name"],
            expected_value["getInHouseInquiryResponse"]["parameters"]["customerName"],
        )
        self.assertEqual(
            response["data"]["bank_account_info"]["status"],
            expected_value["getInHouseInquiryResponse"]["parameters"]["accountStatus"],
        )
        self.assertEqual(
            response["data"]["bank_account_info"]["account_type"],
            expected_value["getInHouseInquiryResponse"]["parameters"]["accountType"],
        )
        self.assertEqual(response["data"]["bank_account_info"]["type"], "BANK_ACCOUNT")

    # end def

    @patch("requests.request")
    def test_get_inhouse_inquiry_bank_account_failed(self, mock_post):
        """ test function to get inhouse inquiry but failed"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getInHouseInquiryResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0000",
                    "responseMessage": "Request Failed",
                    "errorMessage": "Some error message",
                    "responseTimestamp": "2017-09-07T14:10:23.431Z",
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBank(access_token).get_inhouse_inquiry(
                {"account_no": "12345"}
            )

    # end def

    @patch("requests.request")
    def test_get_inhouse_inquiry_va_account_success(self, mock_post):
        """ test successfull request to get inhouse inquiry"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getInHouseInquiryResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2018-08-19T17:02:05.711Z",
                    "customerName": "VA CREDIT DEBET111111",
                    "accountNumber": "8696000000000146",
                    "accountStatus": "1",
                    "accountType": "007",
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBank(access_token).get_inhouse_inquiry({"account_no": "12345"})
        self.assertEqual(
            response["data"]["bank_account_info"]["account_no"],
            expected_value["getInHouseInquiryResponse"]["parameters"]["accountNumber"],
        )
        self.assertEqual(
            response["data"]["bank_account_info"]["customer_name"],
            expected_value["getInHouseInquiryResponse"]["parameters"]["customerName"],
        )
        self.assertEqual(
            response["data"]["bank_account_info"]["status"],
            expected_value["getInHouseInquiryResponse"]["parameters"]["accountStatus"],
        )
        self.assertEqual(
            response["data"]["bank_account_info"]["account_type"],
            expected_value["getInHouseInquiryResponse"]["parameters"]["accountType"],
        )
        self.assertEqual(
            response["data"]["bank_account_info"]["type"], "VIRTUAL_ACCOUNT"
        )

    # end def

    @patch("requests.request")
    def test_do_payment_success(self, mock_post):
        """ test successfull request to do payment"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "method": "IN_HOUSE",
            "source_account": "113183203",
            "account_no": "115471119",
            "amount": "100500",
            "ref_number": "20170227000000000020",
            "email": "jennie@blackpink.com",
            "clearing_code": "CENAIDJAXXX",
            "account_name": "Jennie",
            "address": "Jl. Buntu",
            "charge_mode": "SOURCE",
        }

        # mock the response here
        expected_value = {
            "doPaymentResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2017-02-27T14:46:55.084Z",
                    "debitAccountNo": 113183203,
                    "creditAccountNo": 115471119,
                    "valueAmount": 100500,
                    "valueCurrency": "IDR",
                    "bankReference": 953403,
                    "customerReference": 20170227000000000020,
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBank(access_token).do_payment(data)
        self.assertEqual(
            response["data"]["transfer_info"]["source_account"],
            expected_value["doPaymentResponse"]["parameters"]["debitAccountNo"],
        )
        self.assertEqual(
            response["data"]["transfer_info"]["destination_account"],
            expected_value["doPaymentResponse"]["parameters"]["creditAccountNo"],
        )
        self.assertEqual(
            response["data"]["transfer_info"]["amount"],
            expected_value["doPaymentResponse"]["parameters"]["valueAmount"],
        )
        self.assertEqual(
            response["data"]["transfer_info"]["ref_number"],
            expected_value["doPaymentResponse"]["parameters"]["customerReference"],
        )
        self.assertEqual(
            response["data"]["transfer_info"]["bank_ref"],
            expected_value["doPaymentResponse"]["parameters"]["bankReference"],
        )

    # end def

    @patch("requests.request")
    def test_do_payment_failed(self, mock_post):
        """ test request to do payment but failed"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "method": "IN_HOUSE",
            "source_account": "113183203",
            "account_no": "115471119",
            "amount": "100500",
            "ref_number": "20170227000000000020",
            "email": "jennie@blackpink.com",
            "clearing_code": "CENAIDJAXXX",
            "account_name": "Jennie",
            "address": "Jl. Buntu",
            "charge_mode": "SOURCE",
        }

        # mock the response here
        expected_value = {
            "doPaymentResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0000",
                    "responseTimestamp": "2017-02-27T14:46:55.084Z",
                    "responseMessage": "Request Failed",
                    "errorMessage": "Some error message",
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBank(access_token).do_payment(data)

    # end def

    @patch("requests.request")
    def test_get_payment_status_success(self, mock_post):
        """ test successful get payment status"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {"request_ref": "20170227000000000020"}

        # mock the response here
        expected_value = {
            "getPaymentStatusResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2017-02-27T15:04:00.927Z",
                    "previousResponse": {
                        "transactionStatus": "Y",
                        "previousResponseCode": "null",
                        "previousResponseMessage": "null",
                        "previousResponseTimestamp": "2017-02-27T07:47:14.640Z",
                        "debitAccountNo": 113183203,
                        "creditAccountNo": 115471119,
                        "valueAmount": 100500,
                        "valueCurrency": "IDR",
                    },
                    "bankReference": 953403,
                    "customerReference": 20170227000000000020,
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBank(access_token).get_payment_status(data)
        self.assertEqual(
            response["data"]["payment_info"]["status"],
            expected_value["getPaymentStatusResponse"]["parameters"][
                "previousResponse"
            ]["transactionStatus"],
        )
        self.assertEqual(
            response["data"]["payment_info"]["source_account"],
            expected_value["getPaymentStatusResponse"]["parameters"][
                "previousResponse"
            ]["debitAccountNo"],
        )
        self.assertEqual(
            response["data"]["payment_info"]["destination_account"],
            expected_value["getPaymentStatusResponse"]["parameters"][
                "previousResponse"
            ]["creditAccountNo"],
        )
        self.assertEqual(
            response["data"]["payment_info"]["amount"],
            expected_value["getPaymentStatusResponse"]["parameters"][
                "previousResponse"
            ]["valueAmount"],
        )

    @patch("requests.request")
    def test_get_payment_status_failed(self, mock_post):
        """ test failed get payment status """
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {"request_ref": "20170227000000000020"}

        # mock the response here
        expected_value = {
            "getPaymentStatusResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0000",
                    "responseMessage": "Request Failed",
                    "responseTimestamp": "2017-02-27T15:04:00.927Z",
                    "errorMessage": "Some Error Message",
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBank(access_token).get_payment_status(data)

    @patch("requests.request")
    def test_get_interbank_inquiry_success(self, mock_post):
        """ test successful interbank inquiry request"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "ref_number": "20170227000000000020",
            "source_account": "113183203",
            "bank_code": "014",
            "account_no": "3333333333",
        }

        # mock the response here
        expected_value = {
            "getInterbankInquiryResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2017-05-08T14:57:51.963Z",
                    "destinationAccountNum": "113183203",
                    "destinationAccountName": "DUMMY NAME",
                    "destinationBankName": "BCA",
                    "retrievalReffNum": 100000000097,
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBank(access_token).get_interbank_inquiry(data)
        self.assertEqual(
            response["data"]["inquiry_info"]["account_no"],
            expected_value["getInterbankInquiryResponse"]["parameters"][
                "destinationAccountNum"
            ],
        )
        self.assertEqual(
            response["data"]["inquiry_info"]["account_name"],
            expected_value["getInterbankInquiryResponse"]["parameters"][
                "destinationAccountName"
            ],
        )
        self.assertEqual(
            response["data"]["inquiry_info"]["transfer_bank_name"],
            expected_value["getInterbankInquiryResponse"]["parameters"][
                "destinationBankName"
            ],
        )
        self.assertEqual(
            response["data"]["inquiry_info"]["transfer_ref"],
            expected_value["getInterbankInquiryResponse"]["parameters"][
                "retrievalReffNum"
            ],
        )

    # end def

    @patch("requests.request")
    def test_get_interbank_inquiry_failed(self, mock_post):
        """ test failed interbank inquiry"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "ref_number": "20170227000000000020",
            "source_account": "113183203",
            "bank_code": "014",
            "account_no": "3333333333",
        }

        # mock the response here
        expected_value = {
            "getInterbankInquiryResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0000",
                    "responseMessage": "Error",
                    "errorMessage": "Some error message",
                    "responseTimestamp": "2017-05-08T14:57:51.963Z",
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBank(access_token).get_interbank_inquiry(data)

    # end def

    @patch("requests.request")
    def test_get_interbank_payment_success(self, mock_post):
        """ test successful interbank payment request"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "ref_number": "20170227000000000020",
            "amount": "10000",
            "source_account": "115471119",
            "account_no": "3333333333",
            "account_name": "Jennie",
            "bank_code": "014",
            "bank_name": "BCA",
            "transfer_ref": "100000000024",
        }

        expected_value = {
            "getInterbankPaymentResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2017-03-01T11:45:02.062Z",
                    "destinationAccountNum": 3333333333,
                    "destinationAccountName": "BENEFICIARY NAME",
                    "customerReffNum": 100000000011,
                    "accountName": "BPK JONOMADE MADEMADEMADEMADE",
                },
            }
        }
        # mock the response here
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBank(access_token).get_interbank_payment(data)
        self.assertEqual(
            response["data"]["transfer_info"]["account_no"],
            expected_value["getInterbankPaymentResponse"]["parameters"][
                "destinationAccountNum"
            ],
        )
        self.assertEqual(
            response["data"]["transfer_info"]["account_name"],
            expected_value["getInterbankPaymentResponse"]["parameters"][
                "destinationAccountName"
            ],
        )
        self.assertEqual(
            response["data"]["transfer_info"]["ref_number"],
            expected_value["getInterbankPaymentResponse"]["parameters"][
                "customerReffNum"
            ],
        )

    # end def

    @patch("requests.request")
    def test_get_interbank_payment_failed(self, mock_post):
        """ test failed interbank payment"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "ref_number": "20170227000000000020",
            "amount": "10000",
            "source_account": "115471119",
            "account_no": "3333333333",
            "account_name": "Jennie",
            "bank_code": "014",
            "bank_name": "BCA",
            "transfer_ref": "100000000024",
        }

        expected_value = {
            "getInterbankPaymentResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0000",
                    "responseMessage": "Request Failed",
                    "responseTimestamp": "2017-02-27T15:04:00.927Z",
                    "errorMessage": "Some Error Message",
                },
            }
        }
        # mock the response here
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBank(access_token).get_interbank_payment(data)

    # end def

    @patch("requests.request")
    def test_bni_transfer_success(self, mock_post):
        """ test successfull transfer between BNI to BNI"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "source_account": "113183203",
            "account_no": "115471119",
            "amount": "100500",
            "bank_code": "009",
            "ref_number": None,
        }

        # mock the response here
        expected_value = {
            "doPaymentResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2017-02-27T14:46:55.084Z",
                    "debitAccountNo": 113183203,
                    "creditAccountNo": 115471119,
                    "valueAmount": 100500,
                    "valueCurrency": "IDR",
                    "bankReference": 953403,
                    "customerReference": 20170227000000000020,
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBank(access_token).transfer(data)
        self.assertEqual(
            response["data"]["transfer_info"]["source_account"],
            expected_value["doPaymentResponse"]["parameters"]["debitAccountNo"],
        )
        self.assertEqual(
            response["data"]["transfer_info"]["destination_account"],
            expected_value["doPaymentResponse"]["parameters"]["creditAccountNo"],
        )
        self.assertEqual(
            response["data"]["transfer_info"]["amount"],
            expected_value["doPaymentResponse"]["parameters"]["valueAmount"],
        )
        self.assertEqual(
            response["data"]["transfer_info"]["ref_number"],
            expected_value["doPaymentResponse"]["parameters"]["customerReference"],
        )
        self.assertEqual(
            response["data"]["transfer_info"]["bank_ref"],
            expected_value["doPaymentResponse"]["parameters"]["bankReference"],
        )

    # end def

    @patch("requests.request")
    def test_bni_transfer_failed(self, mock_post):
        """ test transfer between BNI to BNI but raise and error"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "source_account": "113183203",
            "account_no": "115471119",
            "amount": "100500",
            "bank_code": "009",
            "ref_number": None,
        }

        # mock the response here
        expected_value = {
            "doPaymentResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0000",
                    "responseMessage": "Request Failed",
                    "responseTimestamp": "2017-02-27T15:04:00.927Z",
                    "errorMessage": "Some Error Message",
                },
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            CoreBank(access_token).transfer(data)

    # end def

    @patch("requests.request")
    def test_hold_amount_success(self, mock_post):
        """ test successfull hold amount on BNI transaction """
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "request_ref": "113183203",
            "account_no": "115471119",
            "amount": "11111",
        }

        # mock the response here
        expected_value = {
            "holdAmountResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0001",
                    "responseMessage": "Request has been processed successfully",
                    "responseTimestamp": "2017-09-25T14:45:47.746Z",
                    "accountOwner": "Nama : ROBERT NARO",
                    "bankReference": 513621,
                    "customerReference": 20170504153218296,
                },
            }
        }

        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBank(access_token).hold_amount(data)
        self.assertEqual(
            response["data"]["payment_info"]["customer_name"],
            expected_value["holdAmountResponse"]["parameters"]["accountOwner"],
        )
        self.assertEqual(
            response["data"]["payment_info"]["bank_ref"],
            expected_value["holdAmountResponse"]["parameters"]["bankReference"],
        )
        self.assertEqual(
            response["data"]["payment_info"]["ref_number"],
            expected_value["holdAmountResponse"]["parameters"]["customerReference"],
        )

    # end def

    @patch("requests.request")
    def test_hold_amount_failed(self, mock_post):
        """ test failed hold amount on BNI transaction """
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "request_ref": "113183203",
            "account_no": "115471119",
            "amount": "11111",
        }

        # mock the response here
        expected_value = {
            "holdAmountResponse": {
                "clientId": "MODANA",
                "parameters": {
                    "responseCode": "0011",
                    "responseMessage": "Previous identical request has been processed successfully",
                    "errorMessage": "Record is paid",
                    "responseTimestamp": "2019-03-11T12:54:35.729Z",
                    "customerReference": "2019031104484653628",
                },
            }
        }

        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBank(access_token).hold_amount(data)


# end class

if __name__ == "__main__":
    unittest.main(verbosity=2)
