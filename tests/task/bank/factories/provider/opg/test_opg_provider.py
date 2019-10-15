import pytest
from unittest.mock import Mock, patch

from task.bank.lib.provider import ProviderError
from task.bank.factories.provider.opg.provider import (
    BNIOpgProvider,
    BNIOpgProviderBuilder
)

from app.config.external.bank import BNI_OPG


class TestBNIOpgProviderBuilder:

    @patch("requests.request")
    def test_authorize(self, mock_request):
        expected_value = {
            "access_token": "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2",
            "token_type": "Bearer",
            "expires_in": 3599,
            "scope": "resource.WRITE resource.READ"
        }

        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        builder = BNIOpgProviderBuilder()
        result = builder.authorize()
        assert result == "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"


class TestMockBNIOpgProvider:
    """ Test class for BNI OPG Provider """

    def test_api_name_to_full_url(self):
        result = BNIOpgProvider("some-access-token").api_name_to_full_url("GET_BALANCE")
        assert result == "https://apidev.bni.co.id:8066/H2H/v2/getbalance?access_token=some-access-token"

    def test_prepare_request(self):
        """ make sure by passing api_name we get the designated request object
        !"""
        payload = {
            "api_name": "GET_BALANCE",
            "method": "POST",
            "payload": {"somepayload": "test"}
        }
        result = BNIOpgProvider("some-access-token").prepare_request(**payload)
        request = result.to_representation()
        assert request["url"]
        assert request["method"]
        assert request["data"]

    @patch("requests.request")
    def test_get_balance_success(self, mock_request):
        """ test success get balance from BNI OPG"""
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

        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        result = BNIOpgProvider(access_token).get_balance("123456")
        assert result["bank_account_info"]
        assert result["bank_account_info"]["customer_name"]
        assert result["bank_account_info"]["balance"]

    @patch("requests.request")
    def test_get_balance_failed(self, mock_request):
        """ test fail to get balance from BNI OPG"""
        expected_value = {
            "getBalanceResponse": {
                "clientId": "BNISERVICE",
                "parameters": {
                    "responseCode": "0000",
                    "errorMessage": "Unknown Output",
                    "responseMessage": "Request failed",
                    "responseTimestamp": "2017-02-24T14:12:25.871Z",
                }
            }
        }

        mock_request.return_value = Mock(status_code=400)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        with pytest.raises(ProviderError):
            BNIOpgProvider(access_token).get_balance("123456")

    @patch("requests.request")
    def test_get_inhouse_inquiry(self, mock_request):
        """ test get account information from BNI OPG"""
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

        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        result = BNIOpgProvider(access_token).get_inhouse_inquiry("123456")

        assert result["bank_account_info"]
        assert result["bank_account_info"]["account_no"]
        assert result["bank_account_info"]["customer_name"]
        assert result["bank_account_info"]["status"]
        assert result["bank_account_info"]["account_type"]
        assert result["bank_account_info"]["type"]

    @patch("requests.request")
    def test_get_inhouse_inquiry_failed(self, mock_request):
        """ test failed to get account inquiry from BNI OPG"""
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

        mock_request.return_value = Mock(status_code=400)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        with pytest.raises(ProviderError):
            BNIOpgProvider(access_token).get_inhouse_inquiry("123456")

    
    @patch("requests.request")
    def test_do_payment_success(self, mock_request):
        """ test success do payment from BNI OPG"""
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

        data = {
            "method": "IN_HOUSE",
            "source": "113183203",
            "destination": "115471119",
            "amount": "100500",
            "ref_number": "20170227000000000020",
            "email": "jennie@blackpink.com",
            "clearing_code": "CENAIDJAXXX",
            "account_name": "Jennie",
            "address": "Jl. Buntu",
            "charge_mode": "SOURCE",
        }

        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        result = BNIOpgProvider(access_token).do_payment(**data)
        assert result["transfer_info"]
        assert result["transfer_info"]["source_account"]
        assert result["transfer_info"]["destination_account"]
        assert result["transfer_info"]["amount"]
        assert result["transfer_info"]["ref_number"]
        assert result["transfer_info"]["bank_ref"]

    
    @patch("requests.request")
    def test_do_payment_failed(self, mock_request):
        """ test fail to do payment from BNI OPG"""
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

        data = {
            "method": "IN_HOUSE",
            "source": "113183203",
            "destination": "115471119",
            "amount": "100500",
            "ref_number": "20170227000000000020",
            "email": "jennie@blackpink.com",
            "clearing_code": "CENAIDJAXXX",
            "account_name": "Jennie",
            "address": "Jl. Buntu",
            "charge_mode": "SOURCE",
        }

        mock_request.return_value = Mock(status_code=400)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        with pytest.raises(ProviderError):
            BNIOpgProvider(access_token).do_payment(**data)

    @patch("requests.request")
    def test_get_payment_status_success(self, mock_request):
        """ test success to get payment status from BNI OPG"""
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

        data = {"request_ref": "20170227000000000020"}

        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        result = BNIOpgProvider(access_token).get_payment_status(**data)

        assert result["payment_info"]
        assert result["payment_info"]["status"]
        assert result["payment_info"]["source_account"]
        assert result["payment_info"]["destination_account"]
        assert result["payment_info"]["amount"]

    @patch("requests.request")
    def test_get_payment_status_failed(self, mock_request):
        """ test failed to get payment status from BNI OPG"""
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

        data = {"request_ref": "20170227000000000020"}

        mock_request.return_value = Mock(status_code=400)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        with pytest.raises(ProviderError):
            BNIOpgProvider(access_token).get_payment_status(**data)

    @patch("requests.request")
    def test_get_interbank_inquiry_success(self, mock_request):
        """ test succesfully get interbank inquiry from BNI OPG"""
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

        data = {
            "ref_number": "20170227000000000020",
            "source": "113183203",
            "bank_code": "014",
            "destination": "3333333333",
        }

        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        result = BNIOpgProvider(access_token).get_interbank_inquiry(**data)
        assert result["inquiry_info"]
        assert result["inquiry_info"]["account_no"]
        assert result["inquiry_info"]["account_name"]
        assert result["inquiry_info"]["transfer_bank_name"]
        assert result["inquiry_info"]["transfer_ref"]
        assert result["request_ref"]

    @patch("requests.request")
    def test_get_interbank_inquiry_failed(self, mock_request):
        """ test failed get interbank inquiry from BNI OPG"""
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

        data = {
            "ref_number": "20170227000000000020",
            "source": "113183203",
            "bank_code": "014",
            "destination": "3333333333",
        }

        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        with pytest.raises(ProviderError):
            BNIOpgProvider(access_token).get_interbank_inquiry(**data)

    @patch("requests.request")
    def test_interbank_payment_success(self, mock_request):
        """ test failed get interbank payment success from BNI OPG"""
        # mock the response here
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

        data = {
            "ref_number": "20170227000000000020",
            "amount": "10000",
            "source": "115471119",
            "destination": "3333333333",
            "destination_name": "Jennie",
            "bank_code": "014",
            "bank_name": "BCA",
            "transfer_ref": "100000000024",
        }


        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        result = BNIOpgProvider(access_token).interbank_payment(**data)
        assert result["transfer_info"]
        assert result["transfer_info"]["account_no"]
        assert result["transfer_info"]["account_name"]
        assert result["transfer_info"]["ref_number"]
        assert result["request_ref"]

    @patch("requests.request")
    def test_interbank_payment_failed(self, mock_request):
        """ test failed get interbank payment success from BNI OPG"""
        # mock the response here
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

        data = {
            "ref_number": "20170227000000000020",
            "amount": "10000",
            "source": "115471119",
            "destination": "3333333333",
            "destination_name": "Jennie",
            "bank_code": "014",
            "bank_name": "BCA",
            "transfer_ref": "100000000024",
        }

        mock_request.return_value = Mock(status_code=400)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        with pytest.raises(ProviderError):
            BNIOpgProvider(access_token).interbank_payment(**data)

    @patch("requests.request")
    def test_bni_transfer_success(self, mock_request):
        """ test successfully transfer from bni to bni"""
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

        data = {
            "source": "113183203",
            "destination": "115471119",
            "amount": "100500",
            "bank_code": "009",
            "inquiry_ref_number": "12345678910",
            "transfer_ref_number": "12345678910"
        }

        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        result = BNIOpgProvider(access_token).transfer(data)
        assert result["transfer_info"]
        assert result["transfer_info"]["source_account"]
        assert result["transfer_info"]["destination_account"]
        assert result["transfer_info"]["amount"]
        assert result["transfer_info"]["ref_number"]
        assert result["transfer_info"]["bank_ref"]
        assert result["request_ref"]

    @patch("requests.request")
    def test_bni_transfer_failed(self, mock_request):
        """ test failed to transfer from bni to bni"""
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

        data = {
            "source": "113183203",
            "destination": "115471119",
            "amount": "100500",
            "bank_code": "009",
            "inquiry_ref_number": "12345678910",
            "transfer_ref_number": "12345678910"
        }

        mock_request.return_value = Mock(status_code=400)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        with pytest.raises(ProviderError):
            BNIOpgProvider(access_token).transfer(data)

    @patch("requests.request")
    def test_transfer_bni(self, mock_request):
        """ test to transfer from bni to bni"""
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
                }
            }
        }

        data = {
            "source": "113183203",
            "destination": "115471119",
            "amount": "100500",
            "bank_code": "009",
            "inquiry_ref_number": "12345678910",
            "transfer_ref_number": "12345678910"
        }

        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        result = BNIOpgProvider(access_token).transfer(data)
        assert result["transfer_info"]
        assert result["transfer_info"]["source_account"]
        assert result["transfer_info"]["destination_account"]
        assert result["transfer_info"]["amount"]
        assert result["transfer_info"]["ref_number"]
        assert result["transfer_info"]["bank_ref"]
        assert result["request_ref"]

    @patch("requests.request")
    def test_hold_amount_success(self, mock_request):
        """ test success to transfer from bni to bni"""
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

        data = {
            "ref_number": "113183203",
            "account_no": "115471119",
            "amount": "11111",
        }

        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        result = BNIOpgProvider(access_token).hold_amount(**data)

        assert result["payment_info"]
        assert result["payment_info"]["customer_name"]
        assert result["payment_info"]["bank_ref"]
        assert result["payment_info"]["ref_number"]

    @patch("requests.request")
    def test_hold_amount_failed(self, mock_request):
        """ test failed to transfer from bni to bni"""
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
        data = {
            "ref_number": "113183203",
            "account_no": "115471119",
            "amount": "11111",
        }


        mock_request.return_value = Mock(status_code=200)
        mock_request.return_value.json.return_value = expected_value

        access_token = "x3LyfeWKbeaARhd2PfU4F4OeNi43CrDFdi6XnzScKIuk5VmvFiq0B2"

        with pytest.raises(ProviderError):
            BNIOpgProvider(access_token).hold_amount(**data)
