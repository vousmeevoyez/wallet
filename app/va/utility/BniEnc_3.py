#!/opt/local/bin/python

import time
import json
import string
import math
import base64

class BniEnc:
	TIME_DIFF_LIMIT = 480

	@staticmethod
	def encrypt(json_data, cid, secret):
		t = str(int(time.time()))[::-1]
		return BniEnc.doubleEncrypt(t + "." + json_data, cid, secret)

	@staticmethod
	def decrypt(hashed_string, cid, secret):
		parseStr = BniEnc.doubleDecrypt(hashed_string, cid, secret)
		data = parseStr.split(".", 1)
		if len(data) == 2:
			strrevtime = data[0][::-1]
			if BniEnc.tsDiff(int(strrevtime)):
				return data[1]

		return None

	@staticmethod
	def tsDiff(ts):
		return math.fabs(ts - time.time()) <= BniEnc.TIME_DIFF_LIMIT

	@staticmethod
	def doubleEncrypt(stringObj, cid, secret):
		result = ''
		result = BniEnc.enc(stringObj, cid)
		result = BniEnc.enc(result, secret)
		# result = result.encode('base64').rstrip('=')
		# result = result.translate(str.maketrans('+/', '-_'))
		result = bytes(result, 'utf-8')
		result = base64.b64encode(result)
		return result

	@staticmethod
	def enc(string, key):
		result = ""
		strls = len(string)
		strlk = len(key)
		for i in range(0, strls):
			char = string[i:i+1]
			st = (i % strlk) - 1
			xlen = None if st < 0 else st+1
			keychar = key[st:xlen]
			char = chr((ord(char) + ord(keychar)) % 128)
			result += char

		return result

	@staticmethod
	def doubleDecrypt(string, cid, secret):
		ceils = math.ceil(len(string) / 4.0) * 4
		while (len(string) < ceils):
			string += "="
		string = string.replace('-', '+').replace('_', '/')
		result = base64.b64decode(string)
		result = BniEnc.dec(result, cid)
		result = BniEnc.dec(result, secret)
		return result

	@staticmethod
	def dec(string, key):
		result = ''
		strls = len(string)
		strlk = len(key)
		for i in range(0, strls):
			char = string[i:i+1]
			st = (i % strlk) - 1
			xlen = None if st < 0 else st+1
			keychar = key[st:xlen]
			char = chr((ord(char) - ord(keychar) + 256) % 128)
			result += char

		return result


# cid = "99099"
# secret = "8eafc8687722fdd0ef78942309fcd983"
# xmap ='{"type" : "createbilling", "client_id" : "99099", "trx_id" : "123000003, "trx_amount" : "10000000",\
#  "billing_type" : "z", "customer_name" : "Mr. Marcio Soares", "customer_email" : "marcio@modana.id", "customer_phone" : "08123123123", \
#  "virtual_account" : "9889909912345677", "datetime_expired" : "2018-10-10T16:00:00+07:00", "description" : "Payment of Trx 123000001" }'
# hashing = BniEnc.encrypt(xmap, cid, secret)
# hashing ="JSpPQldMKiIdIR5mDXkJBk4MCk9aVg8cDiIrT0xWFB0OXBASfgVMESsSIRQfVD9JAhQIYmVeTldLSkwCCxJgXA4rQFNOVCooISApGxxPR1EaTlAJHRRhXVtIUwwLCWBlDis3TEFIE0lmY2RaTwQPfFd2DFUTLAY4TVtVfws_HhNGZhEODgBWYVBgT1pZBD9OC1RRKBIcFxUWChxVUVYLHQ5UEwQTC15UWk9VWEx_CT8jQANRY1VWUSxWYQN0C1MfVUxARkEASWNWZFlPUH4AD0V_E1VVCycNHhkaV0lOIhUcKj5LTFYmIisaIA0XQXh-XQMTUF5XTFBbWVsRAXgUKw4jRUxPSSIXHiAhCxNTV00ZT08gEx4GT01dVwoFCldQU1IXBwQBZRErXlxXV0s_eEoSBGRRX1JKWEFlE3sSWVVNZQN1QVZfZFRcHA1bdxYKTgwKT19mTwQmV2cLf0kUYU1hC38NEEdQXl9lUF9BVz8QQEsSZ0pMXmBKXRQPPywKHRNKPHoBZFJjUGBfVA4CPyMMFFNdHg9NTFVeCAp7UWVlYXo8WT5bCB0SVExWBBEGVnp-U2NXRV9RTVF_DwwqJxMiQFRBRSEgKR0YGxhPVmgaVFklGywgGxcQKVlMTQsdDlV_BQQQWlxNT1VjW38PAk19f2NgKiMSHQssQUVNJCEZGU9HT008ICUqIBIlT01IEFVZICELGQ1QSl0EEAZfTUthfxMDAV9jUFBjWiNVRE4LWA1cXV4ZDUdKZgQQfV9WS112DRN7ZlZVUWRQRn4GEFhNVSAiFB5ZYVVeEw"
# decode = BniEnc.decrypt(hashing, cid,secret)

# print(decode)



