# Copyright (c) 2013 Alan McIntyre

import httplib
import json
import decimal

decimal.getcontext().rounding = decimal.ROUND_DOWN
exps = [decimal.Decimal("1e-%d" % i) for i in range(16)]

domain = 'bter.com'

all_pairs = ['btc_cny',
             'ltc_cny',
             'ftc_cny',
             'frc_cny',
             'ppc_cny',
             'trc_cny',
             'wdc_cny',
             'yac_cny',
             'cnc_cny',
             'bqc_cny',
             'ifc_cny',
             'zcc_cny',
             'cmc_cny',
             'jry_cny',
             'ftc_ltc',
             'frc_ltc',
             'ppc_ltc',
             'trc_ltc',
             'nmc_ltc',
             'wdc_ltc',
             'yac_ltc',
             'cnc_ltc',
             'bqc_ltc',
             'ifc_ltc',
             'red_ltc',
             'tix_ltc',
             'ltc_btc',
             'nmc_btc',
             'ppc_btc',
             'trc_btc',
             'frc_btc',
             'ftc_btc',
             'bqc_btc',
             'cnc_btc',
             'btb_btc',
             'yac_btc',
             'wdc_btc',
             'zcc_btc',
             'xpm_btc',
             'zet_btc',
             'src_btc',
             'sav_btc',
             'cdc_btc',
             'cmc_btc',
             'jry_btc',
             'tix_btc',
             'tag_btc',
             'exc_btc',
             'nec_btc',
             'cent_btc',
             'mec_btc',
             'qrk_btc',
             'anc_btc',
             'nvc_btc',
             'buk_btc',
             'myminer_btc',
             'doge_btc' # new!!!! 2/5/13
             ]

all_currencies = list(set(sum([p.split('_') for p in all_pairs], [])))

max_digits = {'btc_cny': {'price': 2, 'amount': 4},
              'ltc_cny': {'price': 2, 'amount': 4},
              'ftc_cny': {'price': 4, 'amount': 5},
              'frc_cny': {'price': 4, 'amount': 5},
              'trc_cny': {'price': 8, 'amount': 3},
              'ppc_cny': {'price': 8, 'amount': 3},
              'wdc_cny': {'price': 8, 'amount': 3},
              'yac_cny': {'price': 8, 'amount': 3},
              'cnc_cny': {'price': 8, 'amount': 3},
              'bqc_cny': {'price': 8, 'amount': 3},
              'ifc_cny': {'price': 7, 'amount': 3},
              'zcc_cny': {'price': 8, 'amount': 3},
              'cmc_cny': {'price': 8, 'amount': 3},
              'jry_cny': {'price': 8, 'amount': 3},
              'ftc_ltc': {'price': 5, 'amount': 3},
              'frc_ltc': {'price': 5, 'amount': 3},
              'ppc_ltc': {'price': 8, 'amount': 3},
              'trc_ltc': {'price': 8, 'amount': 3},
              'nmc_ltc': {'price': 8, 'amount': 3},
              'wdc_ltc': {'price': 8, 'amount': 3},
              'yac_ltc': {'price': 8, 'amount': 3},
              'cnc_ltc': {'price': 8, 'amount': 3},
              'bqc_ltc': {'price': 8, 'amount': 3},
              'ifc_ltc': {'price': 8, 'amount': 3},
              'red_ltc': {'price': 8, 'amount': 3},
              'tix_ltc': {'price': 8, 'amount': 3},
              'ltc_btc': {'price': 5, 'amount': 4},
              'nmc_btc': {'price': 8, 'amount': 3},
              'ppc_btc': {'price': 5, 'amount': 3},
              'trc_btc': {'price': 5, 'amount': 3},
              'frc_btc': {'price': 6, 'amount': 3},
              'ftc_btc': {'price': 5, 'amount': 3},
              'bqc_btc': {'price': 7, 'amount': 2},
              'cnc_btc': {'price': 6, 'amount': 3},
              'btb_btc': {'price': 5, 'amount': 4},
              'yac_btc': {'price': 6, 'amount': 3},
              'wdc_btc': {'price': 7, 'amount': 3},
              'zcc_btc': {'price': 6, 'amount': 3},
              'xpm_btc': {'price': 8, 'amount': 3},
              'zet_btc': {'price': 8, 'amount': 3},
              'src_btc': {'price': 8, 'amount': 3},
              'sav_btc': {'price': 8, 'amount': 3},
              'cdc_btc': {'price': 8, 'amount': 3},
              'cmc_btc': {'price': 8, 'amount': 3},
              'jry_btc': {'price': 8, 'amount': 3},
              'tix_btc': {'price': 8, 'amount': 3},
              'tag_btc': {'price': 5, 'amount': 3},
              'exc_btc': {'price': 8, 'amount': 3},
              'nec_btc': {'price': 8, 'amount': 3},
              'cent_btc': {'price': 7, 'amount': 3},
              'mec_btc': {'price': 8, 'amount': 3},
              'qrk_btc': {'price': 8, 'amount': 3},
              'anc_btc': {'price': 7, 'amount': 3},
              'nvc_btc': {'price': 8, 'amount': 3},
              'buk_btc': {'price': 8, 'amount': 3},
              'myminer_btc': {'price': 4, 'amount': 0},
              'doge_btc' : {'price':8,'amount':4} # not sure if these are the right numbers
              }

# min_orders = {'btc_cny': decimal.Decimal("0.1"),
#               'ltc_cny': decimal.Decimal("0.1"),
#               'ftc_cny': decimal.Decimal("0.1"),
#               'frc_cny': decimal.Decimal("0.1"),
#               'trc_cny': decimal.Decimal("0.1"),
#               'wdc_cny': decimal.Decimal("0.1"),
#               'yac_cny': decimal.Decimal("0.1"),
#               'cnc_cny': decimal.Decimal("0.1"),
#               'ftc_ltc': decimal.Decimal("0.1"),
#               'frc_ltc': decimal.Decimal("0.1"),
#               'ppc_ltc': decimal.Decimal("0.1"),
#               'trc_ltc': decimal.Decimal("0.1"),
#               'nmc_ltc': decimal.Decimal("0.1"),
#               'wdc_ltc': decimal.Decimal("0.1"),
#               'yac_ltc': decimal.Decimal("0.1"),
#               'cnc_ltc': decimal.Decimal("0.1"),
#               'bqc_ltc': decimal.Decimal("0.1"),
#               'ltc_btc': decimal.Decimal("0.1"),
#               'nmc_btc': decimal.Decimal("0.1"),
#               'ppc_btc': decimal.Decimal("0.1"),
#               'trc_btc': decimal.Decimal("0.1"),
#               'frc_btc': decimal.Decimal("0.1"),
#               'ftc_btc': decimal.Decimal("0.1"),
#               'bqc_btc': decimal.Decimal("0.1"),
#               'cnc_btc': decimal.Decimal("0.1"),
#               'btb_btc': decimal.Decimal("0.1"),
#               'yac_btc': decimal.Decimal("0.1"),
#               'wdc_btc': decimal.Decimal("0.1")}

fees = {k: 0.001 for k in max_digits.keys()}


def parseJSONResponse(response):
    def parse_decimal(var):
        return decimal.Decimal(var)

    try:
        r = json.loads(response, parse_float=parse_decimal, parse_int=parse_decimal)
    except Exception as e:
        msg = "Error while attempting to parse JSON response: %s\nResponse:\n%r" % (e, response)
        raise Exception(msg)

    return r


class BTERConnection:
    def __init__(self, timeout=30):
        self.conn = httplib.HTTPSConnection(domain, timeout=timeout)

    def close(self):
        self.conn.close()

    def makeRequest(self, url, method='POST', extra_headers=None, params=''):
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        if extra_headers is not None:
            headers.update(extra_headers)

        self.conn.request(method, url, params, headers)
        response = self.conn.getresponse().read()

        return response

    def makeJSONRequest(self, url, method='POST', extra_headers=None, params=""):
        response = self.makeRequest(url, method, extra_headers, params)
        return parseJSONResponse(response)


def validatePair(pair):
    if pair not in all_pairs:
        if "_" in pair:
            a, b = pair.split("_")
            swapped_pair = "%s_%s" % (b, a)
            if swapped_pair in all_pairs:
                msg = "Unrecognized pair: %r -- did you mean %s?" % (pair, swapped_pair)
                raise Exception(msg)
        raise Exception("Unrecognized pair: %r" % pair)


def truncateAmountDigits(value, digits):
    quantum = exps[digits]
    return decimal.Decimal(value).quantize(quantum)


def truncateAmount(value, pair, price_or_amount):
    return truncateAmountDigits(value, max_digits[pair][price_or_amount])


def formatCurrencyDigits(value, digits):
    s = str(truncateAmountDigits(value, digits))
    dot = s.index(".")
    while s[-1] == "0" and len(s) > dot + 2:
        s = s[:-1]

    return s


def formatCurrency(value, pair, price_or_amount):
    return formatCurrencyDigits(value, max_digits[pair][price_or_amount])


def validateResponse(result, error_handler=None):
    #TODO: Proper error handling with Exception sublcass
    if type(result) is not dict:
        raise Exception('The response is not a dict.')

    if result[u'result'] == u'false' or not result[u'result']:
        if error_handler is None:
            raise Exception(errorMessage(result))
        else:
            result = error_handler(result)

    return result


def errorMessage(result):
    if u'message' in result.keys():
        message = result[u'message']
    elif u'msg' in result.keys():
        message = result[u'msg']
    else:
        message = result
    return message
