# https://auking.s3.ap-southeast-2.amazonaws.com/media/paymentInvoicePdf/2024040502015419-Invoice.pdf
# https://auking.s3.ap-southeast-2.amazonaws.com/media/paymentInvoicePdf/2024040502015419-Invoice.pdf

import hashlib
from urllib.parse import urlencode, quote

# paramsToken = {
# 		'merchant_id': '10088',
#         'authentication_code': 'c3c5134dea12900d29c5deb2d5775162',
#         'merchant_trade_no': '88888888',
#         'total_amount': '15'
# 	}

paramsToken = {
		'notice_id': '1000000088',
        'merchant_trade_no': '88888888',
        'authentication_code': 'c3c5134dea12900d29c5deb2d5775162',
	}

encoded_params = urlencode(paramsToken, quote_via=quote)
md5_hash = hashlib.md5(encoded_params.encode()).hexdigest()

print(md5_hash)
print(md5_hash=='95d7068b3d94c7d644bd02a5c48b5103')


A$198.00
Total Product Price
A$132.30
Total Add-On Service Price
A$15.40
Total Logistics Price
A$43.00
Total Transaction Handling Fee
A$7.30