# support code from https://www.coins-e.com/assets/api/coins-e_api_example.py
# -*- coding: utf-8 -*-

import urllib,urllib2
import hmac
import hashlib
import json
from myutils import get_swapped_order
from Exchange import Exchange
from order import Order

class CoinsE(Exchange):
    """docstring for Coins-e"""
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret
        self.base_api_url = "https://www.coins-e.com/api/v2"
        super(CoinsE, self).__init__()
        self.name = 'COINS-E'
        self.trading_fee = 0.002

    # implemented abstract functions
    def get_tradeable_pairs(self):
        tradeable_pairs = []
        markets = self.unauthenticated_request('markets/list/')
        for m in markets['markets']:
            tradeable_pairs.append((m['c1'], m['c2']))
        return tradeable_pairs

    def get_depth(self, base, alt):
        book = { "bids" : [], "asks" : [] }
        pair0 = (base, alt)
        pair, swapped = self.get_validated_pair(pair0)
        newbase, newalt = pair
        slug = newbase + "_" + newalt
        marketdata = self.unauthenticated_request('markets/data/')
        depth = marketdata['markets'][slug]['marketdepth']
        if swapped:
            for bid in depth['bids']:
                o = Order(float(bid['r']), float(bid['q']))
                ask = get_swapped_order(o)
                book['asks'].append(ask)
            for ask in depth['asks']:
                o = Order(float(ask['r']), float(ask['q']))
                bid = get_swapped_order(o)
                book['bids'].append(o)
        else:
            for bid in depth['bids']:
                o = Order(float(bid['r']), float(bid['q']))
                book['bids'].append(o)
            for ask in depth['asks']:
                o = Order(float(ask['r']), float(ask['q']))
                book['asks'].append(o)
        return book

    def get_balance(self, currency):
        data = self.authenticated_request('wallet/' + currency + '/', "getwallet")
        return float(data['wallet']['available'])

    def get_all_balances(self):
        data = self.authenticated_request('wallet/all/', "getwallets")
        balances = {k:float(v["a"]) for k,v in data["wallets"].items()}
        return balances

    def submit_order(self, gc, gv, rc, rv):
        pass
        #order_request = self.authenticated_request('market/%s/' % (working_pair), "neworder", {'order_type':order_type, 'rate':rate, 'quantity':amount,})

    def confirm_order(self, orderID):
#        get_order_request = self.authenticated_request('market/%s/' % (working_pair),"getorder",{'order_id':new_order_request['order']['id']})
#        print get_order_request
        # TODO
        pass

    # COINS-E specific methods

    def unauthenticated_request(self, url_suffix):
        url_request_object = urllib2.Request("%s/%s" % (self.base_api_url, url_suffix))
        response = urllib2.urlopen(url_request_object)
        response_json = {}
        try:
            response_content = response.read()
            response_json = json.loads(response_content)
            return response_json
        finally:
            response.close()
        return "failed"



    def authenticated_request(self, url_suffix, method, post_args={}):
        nonce = 1000
        try:
            f = open('coins-e_nonce', 'r')
            nonce = int(f.readline())
            f.close()
        finally:
            f = open('coins-e_nonce', 'w')
            nonce += 1
            f.write(str(nonce))
            f.close()

        post_args['method'] = method
        post_args['nonce'] = nonce
        post_data = urllib.urlencode(post_args)
        required_sign = hmac.new(self.secret, post_data, hashlib.sha512).hexdigest()
        headers = {}
        headers['key'] = self.api_key
        headers['sign'] = required_sign
        url_request_object = urllib2.Request("%s/%s" % (self.base_api_url, url_suffix),
                                             post_data,
                                             headers)
        response = urllib2.urlopen(url_request_object)


        try:
            response_content = response.read()
            response_json = json.loads(response_content)
            if not response_json['status']:
                print response_content
                print "request failed"
                print response_json['message']

            return response_json
        finally:
            response.close()
        return "failed"


