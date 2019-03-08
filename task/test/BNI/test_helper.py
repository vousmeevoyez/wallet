"""
    BNI Helper
    _____________________
    this is test case where wallet communicate with BNI VA & COre Banking API
"""
#pylint: disable=import-error
import unittest
from unittest.mock import Mock, patch

from datetime import datetime

from task.test.base import BaseTestCase
from app.api import db
from app.api.models import Wallet
from app.api.models import ExternalLog

from task.bank.BNI.helper import VirtualAccount as VirtualAccountHelper
from task.bank.BNI.helper import CoreBank as CoreBankHelper
from task.bank.BNI.utility import remote_call

from task.bank.exceptions.general import *

class TestMockVirtualAccountHelper(BaseTestCase):
    """ This is class to test by mocking all response for e collection helper"""

    @patch.object(VirtualAccountHelper, '_post')
    def test_mock_create_va_success(self, mock_post):
        """
            test function to successfully create va using mock response
            from VirtualAccountHelper._post
        """

        # payload needed to create virtual account
        data = {
            "amount"          : "1500",
            "customer_name"   : "Jennie",
            "customer_phone"  : "081234123111",
            "datetime_expired": datetime.now(),
            "virtual_account" : "12345678",
            "transaction_id"  : "12345678",
        }

        # expected value from BNI server
        expected_value = {
            "status" : "000",
            "data" : {'trx_id': "1234", 'virtual_account': "000211"}
        }

        # replace return value using expected value here
        mock_post.return_value = expected_value

        result = VirtualAccountHelper().create_va("CREDIT", data)
        self.assertEqual(result["status"], "000") # data already existed

    @patch.object(VirtualAccountHelper, '_post')
    def test_mock_create_va_failed(self, mock_post):
        """
            test function to try create va but failed using mock response
            from VirtualAccountHelper._post
        """
        # payload needed to create a va
        data = {
            "amount"          : "1500",
            "customer_name"   : "Jennie",
            "customer_phone"  : "081234123111",
            "datetime_expired": datetime.now(),
            "virtual_account" : "12345678",
            "transaction_id"  : "12345678",
        }


        # replace with mock response here
        mock_post.side_effect = RemoteCallError(Mock())

        with self.assertRaises(ApiError):
            result = VirtualAccountHelper().create_va("CREDIT", data)

    @patch.object(VirtualAccountHelper, '_post')
    def test_mock_create_va_cardless_success(self, mock_post):
        """
            test function to create cardless va using mock response
            from VirtualAccountHelper._post
        """
        # required paylod to create va
        data = {
            "amount"          : "1500",
            "customer_name"   : "Jennie",
            "customer_phone"  : "081234123111",
            "datetime_expired": datetime.now(),
            "virtual_account" : "12345678",
            "transaction_id"  : "12345678",
        }

        # expected value from BNI
        expected_value = {
            "status" : "000",
            "data" : {'trx_id': "1234", 'virtual_account': "000211"}
        }

        # replace normal return_value with expected_value
        mock_post.return_value = expected_value

        result = VirtualAccountHelper().create_va("DEBIT", data)
        self.assertEqual(result["status"], "000") # data already existed

    @patch.object(VirtualAccountHelper, '_post')
    def test_mock_create_va_cardless_failed(self, mock_post):
        """
            test function to try create cardless va but failed using mock response
            from VirtualAccountHelper._post
        """
        # required payload to create va
        data = {
            "amount"          : "1500",
            "customer_name"   : "Jennie",
            "customer_phone"  : "081234123111",
            "datetime_expired": datetime.now(),
            "virtual_account": "12345678",
            "transaction_id"    : "12345678",
        }

        # replace with mock response here
        mock_post.side_effect = RemoteCallError(Mock())

        with self.assertRaises(ApiError):
            result = VirtualAccountHelper().create_va("DEBIT", data)

    @patch.object(VirtualAccountHelper, '_post')
    def test_mock_get_inquiry_success(self, mock_post):
        """
            test function to get va inquiry using mock response
            from VirtualAccountHelper._post
        """
        # use dummy trx_id
        data = {
            "trx_id" : "121",
        }

        # expected_value from bni server
        expected_value = {
            'status' : '000',
            'data': {
                'client_id': '99099',
                'trx_id': '121',
                'virtual_account': '9889909918102605',
                'trx_amount': '1',
                'customer_name': 'Jennie',
                'customer_phone': '',
                'customer_email': '',
                'datetime_created': '2018-10-26 06:39:27',
                'datetime_expired': '2017-10-28 06:39:27',
                'datetime_payment': None,
                'datetime_last_updated': '2018-10-26 06:43:25',
                'payment_ntb': None,
                'payment_amount': '0',
                'va_status': '2',
                'description': '',
                'billing_type': 'j',
                'datetime_created_iso8601': '2018-10-26T06:39:27+07:00',
                'datetime_expired_iso8601': '2017-10-28T06:39:27+07:00',
                'datetime_payment_iso8601': None,
                'datetime_last_updated_iso8601': '2018-10-26T06:43:25+07:00'
            }
        }

        mock_post.return_value = expected_value

        result = VirtualAccountHelper().get_inquiry("CREDIT", data)
        self.assertEqual(result["status"], "000")

    @patch.object(VirtualAccountHelper, '_post')
    def test_mock_get_inquiry_failed(self, mock_post):
        """
            test function to try get va inquiry but failed using mock response
            from VirtualAccountHelper._post
        """
        # dummy trx id
        data = {
            "trx_id"  : "121",
        }

        # replace with mock response here
        mock_post.side_effect = RemoteCallError(Mock())

        with self.assertRaises(ApiError):
            result = VirtualAccountHelper().get_inquiry("CREDIT", data)

    @patch.object(VirtualAccountHelper, '_post')
    def test_mock_update_va_success(self, mock_post):
        """
            test function to try update va using mock response
            from VirtualAccountHelper._post
        """
        data = {
            "trx_id" : "627493687",
            "amount" : "1000",
            "customer_name"    : "Kelvin",
            "datetime_expired" : datetime.now(),
        }

        expected_value = {
            "status" : "000",
            "data": {
                'type': 'updatebilling',
                'client_id': '99099',
                'trx_id': '627493687',
                'trx_amount': '1000',
                'customer_name': 'Kelvin',
                'datetime_expired': '2017-10-29 06:39:27'
            }
        }

        mock_post.return_value = expected_value

        result = VirtualAccountHelper().update_va("CREDIT", data)
        self.assertEqual(result["status"], "000")

    @patch.object(VirtualAccountHelper, '_post')
    def test_mock_update_va_failed(self, mock_post):
        """
            test function to try update va but falied using mock response
            from VirtualAccountHelper._post
        """
        data = {
            "trx_id" : "627493687",
            "amount" : "1000",
            "customer_name"    : "Kelvin",
            "datetime_expired" : datetime.now(),
        }

        mock_post.side_effect = RemoteCallError(Mock())

        with self.assertRaises(ApiError):
            result = VirtualAccountHelper().update_va("CREDIT", data)

    @patch.object(remote_call, "post")
    def test_post_credit_success(self, mock_post):
        """ test success post function to BNI Credit E-Collection"""
        api_name = "API_NAME"
        payload = {
            'client_id': '99099',
            'trx_id': '121',
            'virtual_account': '9889909918102605',
            'trx_amount': '1',
            'customer_name': 'Jennie',
            'customer_phone': '',
            'customer_email': '',
            'datetime_expired': '2017-10-28 06:39:27',
            'va_status': '2',
            'description': '',
            'billing_type': 'j',
        }
        mock_post.return_value = { "status" : "000", "data" : "test" }
        result = VirtualAccountHelper()._post(api_name, "CREDIT", payload)
        self.assertEqual(result["status"], "000")

    @patch.object(remote_call, "post")
    def test_post_credit_failed(self, mock_post):
        """ test failed post function to BNI Credit E-Collection"""
        api_name = "API_NAME"
        payload = {
            'client_id': '99099',
            'trx_id': '121',
            'virtual_account': '9889909918102605',
            'trx_amount': '1',
            'customer_name': 'Jennie',
            'customer_phone': '',
            'customer_email': '',
            'datetime_expired': '2017-10-28 06:39:27',
            'va_status': '2',
            'description': '',
            'billing_type': 'j',
        }

        mock_post.side_effect = ServicesFailed("some error", Mock())
        with self.assertRaises(RemoteCallError):
            result = VirtualAccountHelper()._post(api_name, "CREDIT", payload)

    @patch.object(remote_call, "post")
    def test_post_cardless_success(self, mock_post):
        """ test success post function to BNI Credit E-Collection"""
        api_name = "API_NAME"
        payload = {
            'client_id': '99099',
            'trx_id': '121',
            'virtual_account': '9889909918102605',
            'trx_amount': '1',
            'customer_name': 'Jennie',
            'customer_phone': '',
            'customer_email': '',
            'datetime_expired': '2017-10-28 06:39:27',
            'va_status': '2',
            'description': '',
            'billing_type': 'j',
        }
        mock_post.return_value = { "status" : "000", "data" : "test" }
        result = VirtualAccountHelper()._post(api_name, "CREDIT", payload)
        self.assertEqual(result["status"], "000")

    @patch.object(remote_call, "post")
    def test_post_cardless_failed(self, mock_post):
        """ test failed post function to BNI Credit E-Collection"""
        api_name = "API_NAME"
        payload = {
            'client_id': '99099',
            'trx_id': '121',
            'virtual_account': '9889909918102605',
            'trx_amount': '1',
            'customer_name': 'Jennie',
            'customer_phone': '',
            'customer_email': '',
            'datetime_expired': '2017-10-28 06:39:27',
            'va_status': '2',
            'description': '',
            'billing_type': 'j',
        }
        mock_post.side_effect = ServicesFailed("some error", Mock())
        with self.assertRaises(RemoteCallError):
            result = VirtualAccountHelper()._post(api_name, "CREDIT", payload)
#end class

class TestMockCoreBankHelper(BaseTestCase):
    """ This is class to test by mocking all response from BNI COre Bank helper"""

    def test_generate_ref_number(self):
        result = CoreBankHelper()._generate_ref_number()
        self.assertTrue(len(result) > 15)
    #end def

    def test__check_response_code(self):
        result = CoreBankHelper()._generate_ref_number()
    #end def

    @patch("requests.post")
    def test_post_form_success(self, mock_post):
        """ test function to mock success post form request and get access
        token"""
        payload = {"grant_type" : "client_credentials"}

        # mock the response here
        expected_value = {
            "access_token": "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2",
            "token_type": "Bearer",
            "expires_in": 3599,
            "scope": "resource.WRITE resource.READ"
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBankHelper()._post("GET_TOKEN", payload)
        self.assertEqual(response["data"], expected_value)
    #end def

    @patch("requests.post")
    def test_post_form_failed(self, mock_post):
        """ test function to mock failed post form request, because server
        return 400"""
        payload = {"grant_type" : "client_credentials"}

        # mock the response here
        expected_value = {
            "message": "Some Error"
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ServicesFailed):
            response = CoreBankHelper()._post("GET_TOKEN", payload)
    #end def

    @patch("requests.post")
    def test_post_json_success(self, mock_post):
        """ test function to mock success post json request"""
        payload = {
            "accountNo" : "11547119",
        }

        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getBalanceResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode"     : "0001",
                    "responseMessage"  : "Request has been processed successfully",
                    "responseTimestamp": "2017-02-24T14:12:25.871Z",
                    "customerName"     : "Bpk JONOMADE MADEMADEMADEMADE IMAMADE",
                    "accountCurrency"  : "IDR",
                    "accountBalance"   : 16732765949981
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBankHelper(access_token)._post("GET_BALANCE", payload)
        self.assertEqual(response["data"], expected_value)
    #end def

    @patch("requests.post")
    def test_get_token_success(self, mock_post):
        """ test function to get token from BNI server"""
        # mock the response here
        expected_value = {
            "access_token": "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2",
            "token_type": "Bearer",
            "expires_in": 3599,
            "scope": "resource.WRITE resource.READ"
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        access_token = CoreBankHelper()._get_token()
        self.assertEqual(access_token, expected_value["access_token"])
    #end def

    @patch("requests.post")
    def test_get_balance_success(self, mock_post):
        """ test function to get balance from BNI server using mock response"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getBalanceResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode"     : "0001",
                    "responseMessage"  : "Request has been processed successfully",
                    "responseTimestamp": "2017-02-24T14:12:25.871Z",
                    "customerName"     : "Bpk JONOMADE MADEMADEMADEMADE IMAMADE",
                    "accountCurrency"  : "IDR",
                    "accountBalance"   : 16732765949981
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBankHelper(access_token).get_balance({"account_no" : "12345"})
        self.assertEqual(response["data"]["bank_account_info"]["customer_name"],
                         expected_value["getBalanceResponse"]["parameters"]["customerName"])
        self.assertEqual(response["data"]["bank_account_info"]["balance"],
                         expected_value["getBalanceResponse"]["parameters"]["accountBalance"])
    #end def

    @patch("requests.post")
    def test_get_balance_failed(self, mock_post):
        """ test function that failed to get balance from bni server"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getBalanceResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode"     : "0000",
                    "errorMessage"     : "Unknown Output",
                    "responseMessage"  : "Request failed",
                    "responseTimestamp": "2017-02-24T14:12:25.871Z",
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBankHelper(access_token).get_balance({"account_no" : "12345"})
    #end def

    def test_create_signature(self):
        """ test function that create jwt signature"""
        payload = {
            "clientId": "IDBNIU0FOREJPWA==",
            "accountNo": "0115476117"
        }
        result = CoreBankHelper()._create_signature(payload)
        self.assertTrue(isinstance(result, str))
    #end def

    @patch("requests.post")
    def test_get_inhouse_inquiry_bank_account_success(self, mock_post):
        """ test function to get successful inhouse inquiry"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getInHouseInquiryResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode"     : "0001",
                    "responseMessage"  : "Request has been processed successfully",
                    "responseTimestamp": "2017-09-07T14:10:23.431Z",
                    "customerName"     : "Bpk JONOMADE MADEMADEMADEMADE IMAMADE",
                    "accountCurrency"  : "IDR",
                    "accountNumber"    : "0115475045",
                    "accountStatus"    : "BUKA",
                    "accountType"      : "DEP"
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBankHelper(access_token).get_inhouse_inquiry({"account_no" : "12345"})
        self.assertEqual(response["data"]["bank_account_info"]["account_no"],
                         expected_value["getInHouseInquiryResponse"]["parameters"]["accountNumber"])
        self.assertEqual(response["data"]["bank_account_info"]["customer_name"],
                         expected_value["getInHouseInquiryResponse"]["parameters"]["customerName"])
        self.assertEqual(response["data"]["bank_account_info"]["status"],
                         expected_value["getInHouseInquiryResponse"]["parameters"]["accountStatus"])
        self.assertEqual(response["data"]["bank_account_info"]["account_type"],
                         expected_value["getInHouseInquiryResponse"]["parameters"]["accountType"])
        self.assertEqual(response["data"]["bank_account_info"]["type"], "BANK_ACCOUNT")
    #end def

    @patch("requests.post")
    def test_get_inhouse_inquiry_bank_account_failed(self, mock_post):
        """ test function to get inhouse inquiry but failed"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getInHouseInquiryResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode"     : "0000",
                    "responseMessage"  : "Request Failed",
                    "errorMessage"     : "Some error message",
                    "responseTimestamp": "2017-09-07T14:10:23.431Z",
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBankHelper(access_token).get_inhouse_inquiry({"account_no" : "12345"})
    #end def

    @patch("requests.post")
    def test_get_inhouse_inquiry_va_account_success(self, mock_post):
        """ test successfull request to get inhouse inquiry"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # mock the response here
        expected_value = {
            "getInHouseInquiryResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode"     : "0001",
                    "responseMessage"  : "Request has been processed successfully",
                    "responseTimestamp": "2018-08-19T17:02:05.711Z",
                    "customerName"     : "VA CREDIT DEBET111111",
                    "accountNumber"    : "8696000000000146",
                    "accountStatus"    : "1",
                    "accountType"      : "007"
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBankHelper(access_token).get_inhouse_inquiry({"account_no" : "12345"})
        self.assertEqual(response["data"]["bank_account_info"]["account_no"],
                         expected_value["getInHouseInquiryResponse"]["parameters"]["accountNumber"])
        self.assertEqual(response["data"]["bank_account_info"]["customer_name"],
                         expected_value["getInHouseInquiryResponse"]["parameters"]["customerName"])
        self.assertEqual(response["data"]["bank_account_info"]["status"],
                         expected_value["getInHouseInquiryResponse"]["parameters"]["accountStatus"])
        self.assertEqual(response["data"]["bank_account_info"]["account_type"],
                         expected_value["getInHouseInquiryResponse"]["parameters"]["accountType"])
        self.assertEqual(response["data"]["bank_account_info"]["type"], "VIRTUAL_ACCOUNT")
    #end def

    @patch("requests.post")
    def test_do_payment_success(self, mock_post):
        """ test successfull request to do payment"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "method" : "IN_HOUSE",
            "source_account" : "113183203",
            "account_no"     : "115471119",
            "amount"         : "100500",
            "ref_number"     : "20170227000000000020",
            "email"          : "jennie@blackpink.com",
            "clearing_code"  : "CENAIDJAXXX",
            "account_name"   : "Jennie",
            "address"        : "Jl. Buntu",
            "charge_mode"    : "SOURCE",
        }

        # mock the response here
        expected_value = {
            "doPaymentResponse" : {
                "clientId" : "BNISERVICE",
                "parameters" : {
                    "responseCode"      : "0001",
                    "responseMessage"   : "Request has been processed successfully",
                    "responseTimestamp" : "2017-02-27T14:46:55.084Z",
                    "debitAccountNo"    : 113183203,
                    "creditAccountNo"   : 115471119,
                    "valueAmount"       : 100500,
                    "valueCurrency"     : "IDR",
                    "bankReference"     : 953403,
                    "customerReference" : 20170227000000000020
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBankHelper(access_token).do_payment(data)
        self.assertEqual(response["data"]["transfer_info"]["source_account"],
                         expected_value["doPaymentResponse"]["parameters"]["debitAccountNo"])
        self.assertEqual(response["data"]["transfer_info"]["destination_account"],
                         expected_value["doPaymentResponse"]["parameters"]["creditAccountNo"])
        self.assertEqual(response["data"]["transfer_info"]["amount"],
                         expected_value["doPaymentResponse"]["parameters"]["valueAmount"])
        self.assertEqual(response["data"]["transfer_info"]["ref_number"],
                         expected_value["doPaymentResponse"]["parameters"]["customerReference"])
        self.assertEqual(response["data"]["transfer_info"]["bank_ref"],
                         expected_value["doPaymentResponse"]["parameters"]["bankReference"])
    #end def

    @patch("requests.post")
    def test_do_payment_failed(self, mock_post):
        """ test request to do payment but failed"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "method" : "IN_HOUSE",
            "source_account" : "113183203",
            "account_no"     : "115471119",
            "amount"         : "100500",
            "ref_number"     : "20170227000000000020",
            "email"          : "jennie@blackpink.com",
            "clearing_code"  : "CENAIDJAXXX",
            "account_name"   : "Jennie",
            "address"        : "Jl. Buntu",
            "charge_mode"    : "SOURCE",
        }

        # mock the response here
        expected_value = {
            "doPaymentResponse" : {
                "clientId" : "BNISERVICE",
                "parameters" : {
                    "responseCode"      : "0000",
                    "responseTimestamp" : "2017-02-27T14:46:55.084Z",
                    "responseMessage"  : "Request Failed",
                    "errorMessage"     : "Some error message",
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBankHelper(access_token).do_payment(data)
    #end def

    @patch("requests.post")
    def test_get_payment_status_success(self, mock_post):
        """ test successful get payment status"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "request_ref" : "20170227000000000020",
        }

        # mock the response here
        expected_value = {
            "getPaymentStatusResponse" : {
                "clientId" : "BNISERVICE",
                "parameters" : {
                    "responseCode" : "0001",
                    "responseMessage" : "Request has been processed successfully",
                    "responseTimestamp" : "2017-02-27T15:04:00.927Z",
                    "previousResponse" : {
                        "transactionStatus" : "Y",
                        "previousResponseCode" : "null",
                        "previousResponseMessage" : "null",
                        "previousResponseTimestamp" : "2017-02-27T07:47:14.640Z",
                        "debitAccountNo" : 113183203,
                        "creditAccountNo" : 115471119,
                        "valueAmount" : 100500,
                        "valueCurrency" : "IDR"
                    },
                    "bankReference" : 953403,
                    "customerReference" : 20170227000000000020
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBankHelper(access_token).get_payment_status(data)
        self.assertEqual(response["data"]["payment_info"]["status"],
                         expected_value["getPaymentStatusResponse"]["parameters"]\
                         ["previousResponse"]["transactionStatus"])
        self.assertEqual(response["data"]["payment_info"]["source_account"],
                         expected_value["getPaymentStatusResponse"]["parameters"]\
                         ["previousResponse"]["debitAccountNo"])
        self.assertEqual(response["data"]["payment_info"]["destination_account"],
                         expected_value["getPaymentStatusResponse"]["parameters"]\
                         ["previousResponse"]["creditAccountNo"])
        self.assertEqual(response["data"]["payment_info"]["amount"],
                         expected_value["getPaymentStatusResponse"]["parameters"]\
                         ["previousResponse"]["valueAmount"])

    @patch("requests.post")
    def test_get_payment_status_failed(self, mock_post):
        """ test failed get payment status """
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "request_ref" : "20170227000000000020",
        }

        # mock the response here
        expected_value = {
            "getPaymentStatusResponse" : {
                "clientId" : "BNISERVICE",
                "parameters" : {
                    "responseCode"      : "0000",
                    "responseMessage"   : "Request Failed",
                    "responseTimestamp" : "2017-02-27T15:04:00.927Z",
                    "errorMessage"      : "Some Error Message"
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBankHelper(access_token).get_payment_status(data)

    @patch("requests.post")
    def test_get_interbank_inquiry_success(self, mock_post):
        """ test successful interbank inquiry request"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "ref_number"     : "20170227000000000020",
            "source_account" : "113183203",
            "bank_code"      : "014",
            "account_no"     : "3333333333",
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
                    "retrievalReffNum": 100000000097
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBankHelper(access_token).get_interbank_inquiry(data)
        self.assertEqual(response["data"]["inquiry_info"]["account_no"],
                         expected_value["getInterbankInquiryResponse"]\
                         ["parameters"]["destinationAccountNum"])
        self.assertEqual(response["data"]["inquiry_info"]["account_name"],
                         expected_value["getInterbankInquiryResponse"]\
                         ["parameters"]["destinationAccountName"])
        self.assertEqual(response["data"]["inquiry_info"]["transfer_bank_name"],
                         expected_value["getInterbankInquiryResponse"]\
                         ["parameters"]["destinationBankName"])
        self.assertEqual(response["data"]["inquiry_info"]["transfer_ref"],
                         expected_value["getInterbankInquiryResponse"]\
                         ["parameters"]["retrievalReffNum"])
    #end def

    @patch("requests.post")
    def test_get_interbank_inquiry_failed(self, mock_post):
        """ test failed interbank inquiry"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "ref_number"     : "20170227000000000020",
            "source_account" : "113183203",
            "bank_code"      : "014",
            "account_no"     : "3333333333",
        }

        # mock the response here
        expected_value = {
            "getInterbankInquiryResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode"     : "0000",
                    "responseMessage"  : "Error",
                    "errorMessage"     : "Some error message",
                    "responseTimestamp": "2017-05-08T14:57:51.963Z",
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBankHelper(access_token).get_interbank_inquiry(data)
    #end def

    @patch("requests.post")
    def test_get_interbank_payment_success(self, mock_post):
        """ test successful interbank payment request"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "ref_number"     : "20170227000000000020",
            "amount"         : "10000",
            "source_account" : "115471119",
            "account_no"     : "3333333333",
            "account_name"   : "Jennie",
            "bank_code"      : "014",
            "bank_name"      : "BCA",
            "transfer_ref"   : "100000000024",
        }

        expected_value = {
            "getInterbankPaymentResponse" : {
                "clientId" : "BNISERVICE",
                "parameters" : {
                    "responseCode" : "0001",
                    "responseMessage" : "Request has been processed successfully",
                    "responseTimestamp" : "2017-03-01T11:45:02.062Z",
                    "destinationAccountNum" : 3333333333,
                    "destinationAccountName" : "BENEFICIARY NAME",
                    "customerReffNum" : 100000000011,
                    "accountName" : "BPK JONOMADE MADEMADEMADEMADE"
                }
            }
        }
        # mock the response here
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBankHelper(access_token).get_interbank_payment(data)
        self.assertEqual(response["data"]["transfer_info"]["account_no"],
                         expected_value["getInterbankPaymentResponse"]\
                         ["parameters"]["destinationAccountNum"])
        self.assertEqual(response["data"]["transfer_info"]["account_name"],
                         expected_value["getInterbankPaymentResponse"]\
                         ["parameters"]["destinationAccountName"])
        self.assertEqual(response["data"]["transfer_info"]["ref_number"],
                         expected_value["getInterbankPaymentResponse"]\
                         ["parameters"]["customerReffNum"])
    #end def

    @patch("requests.post")
    def test_get_interbank_payment_failed(self, mock_post):
        """ test failed interbank payment"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "ref_number"     : "20170227000000000020",
            "amount"         : "10000",
            "source_account" : "115471119",
            "account_no"     : "3333333333",
            "account_name"   : "Jennie",
            "bank_code"      : "014",
            "bank_name"      : "BCA",
            "transfer_ref"   : "100000000024",
        }

        expected_value = {
            "getInterbankPaymentResponse" : {
                "clientId" : "BNISERVICE",
                "parameters" : {
                    "responseCode" : "0000",
                    "responseMessage"   : "Request Failed",
                    "responseTimestamp" : "2017-02-27T15:04:00.927Z",
                    "errorMessage"      : "Some Error Message"
                }
            }
        }
        # mock the response here
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            response = CoreBankHelper(access_token).get_interbank_payment(data)
    #end def

    @patch("requests.post")
    def test_bni_transfer_success(self, mock_post):
        """ test successfull transfer between BNI to BNI"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "source_account": "113183203",
            "account_no"    : "115471119",
            "amount"        : "100500",
            "bank_code"     : "009",
        }

        # mock the response here
        expected_value = {
            "doPaymentResponse" : {
                "clientId" : "BNISERVICE",
                "parameters" : {
                    "responseCode"      : "0001",
                    "responseMessage"   : "Request has been processed successfully",
                    "responseTimestamp" : "2017-02-27T14:46:55.084Z",
                    "debitAccountNo"    : 113183203,
                    "creditAccountNo"   : 115471119,
                    "valueAmount"       : 100500,
                    "valueCurrency"     : "IDR",
                    "bankReference"     : 953403,
                    "customerReference" : 20170227000000000020
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        response = CoreBankHelper(access_token).transfer(data)
        self.assertEqual(response["data"]["transfer_info"]["source_account"],
                         expected_value["doPaymentResponse"]["parameters"]["debitAccountNo"])
        self.assertEqual(response["data"]["transfer_info"]["destination_account"],
                         expected_value["doPaymentResponse"]["parameters"]["creditAccountNo"])
        self.assertEqual(response["data"]["transfer_info"]["amount"],
                         expected_value["doPaymentResponse"]["parameters"]["valueAmount"])
        self.assertEqual(response["data"]["transfer_info"]["ref_number"],
                         expected_value["doPaymentResponse"]["parameters"]["customerReference"])
        self.assertEqual(response["data"]["transfer_info"]["bank_ref"],
                         expected_value["doPaymentResponse"]["parameters"]["bankReference"])
    #end def

    @patch("requests.post")
    def test_bni_transfer_failed(self, mock_post):
        """ test transfer between BNI to BNI but raise and error"""
        # use mock token here
        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        # define required data to execute transfer here
        data = {
            "source_account": "113183203",
            "account_no"    : "115471119",
            "amount"        : "100500",
            "bank_code"     : "009",
        }

        # mock the response here
        expected_value = {
            "doPaymentResponse" : {
                "clientId" : "BNISERVICE",
                "parameters" : {
                    "responseCode" : "0000",
                    "responseMessage"   : "Request Failed",
                    "responseTimestamp" : "2017-02-27T15:04:00.927Z",
                    "errorMessage"      : "Some Error Message"
                }
            }
        }
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = expected_value

        with self.assertRaises(ApiError):
            CoreBankHelper(access_token).transfer(data)
    #end def
#end class

if __name__ == "__main__":
    unittest.main(verbosity=2)
