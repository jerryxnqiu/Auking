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
		'notice_id': '2024050400947567845108310016',
        'merchant_trade_no': '202405041351082',
        'authentication_code': 'lkjh678jGQDJokl9XQHaHIyfuytttqqq',
	}

encoded_params = urlencode(paramsToken, quote_via=quote)
md5_hash = hashlib.md5(encoded_params.encode()).hexdigest()

print(md5_hash)
print(md5_hash=='31efa335db208c42f200db78271fa8d1')