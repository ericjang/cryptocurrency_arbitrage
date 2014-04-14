# Simple Python API for CoinEX cryptocurrency exchange
# Author: Eric Jang
# License: GPL
# 17 Jan 2014

import httplib
import urllib, urllib2
import json
import hashlib
import hmac
import time

import requests

class CoinExAPI(object):
    def __init__(self, api_key, api_secret):
        self.base_url = "https://coinex.pw/api/v2/"
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = { "Content-type": "application/json"
                        , "Accept": "application/json"
                        , "User-Agent": "Mozilla/4.0 (compatible; CoinEx API PHP client; "}

    # PUBLIC API METHODS
    def get_currencies(self):
        return self._public_request("currencies")

    def get_trade_pairs(self):
        return self._public_request("trade_pairs")

    def get_orders(self, pairID):
        return self._public_request("orders", {"tradePair":pairID})

    def get_trades(self, pairID):
        return self._public_request("trades", {"tradePair":pairID})

    # SECURE (TRADE) API (requires API keys)
    def submit_order(self, pairID, amount, order_type, rate):
        # coinEX deals in numbers multiplied by 1e8 to avoid floating point
        if order_type == "buy":
            bid = True
        elif order_type == "sell":
            bid = False
        else:
            raise ValueError("type=%s not recognized. Specify either `buy` or `sell`" % (type))

        data = {
        "order" : {
                "trade_pair_id" : pairID,
                "amount" : int(amount * 1e8),
                "bid" : True,
                "rate": int(rate * 1e8)
            }
        }
        datastring = json.dumps(data)
        api_sign = hmac.new(self.api_secret, datastring, hashlib.sha512).hexdigest()

        hh = {
          "API-Key" : self.api_key,
          "API-Sign" : api_sign
        }
        hh.update(self.headers)

        req = requests.post(self.base_url + "orders",
                          data=datastring,
                          headers=hh)
        return req.json()

    def get_order_status(self, orderID):
        return self._public_request("orders/" + str(orderID))

    def cancel_order(self, orderID):
        return self._secure_request("orders/" + str(orderID) + "/cancel", data={})

    def get_own_orders(self):
        return self._secure_request("orders/own")

    def get_balances(self):
        return self._secure_request("balances")

    # HELPER METHODS
    def _public_request(self, api_method, params=None):
        # this is only for GET requests
        if params is None:
            param_string = ""
        else:
            param_string = urllib.urlencode(params)
        url = "%s%s?%s" % (self.base_url, api_method, param_string)
        return self._req(url, headers=self.headers)

    def _secure_request(self, api_method, data=None):
        datastring = "" if data is None else json.dumps(data)
        api_sign = hmac.new(self.api_secret, datastring, hashlib.sha512).hexdigest()
        headers = {
            "API-Key" : self.api_key,
            "API-Sign" : api_sign
        }
        headers.update(self.headers)
        url = "%s%s" % (self.base_url, api_method)
        if data is None:
            return self._req(url, headers=headers) # secure GET request
        else:
            return self._req(url, headers=headers, datastring=datastring) # secure POST request

    def _req(self, url, headers, datastring=None):
        if datastring is None:
            request = urllib2.Request(url, headers=headers) # GET request
        else:
            request = urllib2.Request(url, datastring, headers=headers) # POST request
        response = urllib2.urlopen(request)
        try:
            response_content = response.read()
            response_json = json.loads(response_content)
            return response_json
        except urllib2.HTTPError, err:
            print(err.code)
        finally:
            response.close()
        return "failed"


