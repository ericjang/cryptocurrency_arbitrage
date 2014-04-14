# -*- coding: utf-8 -*-
import urllib,urllib2
from datetime import datetime
import time
from decimal import *
import hmac
import hashlib
import json

COINS_E_API_KEY = "32738a3fb2179b177f82cf7303f4bdbc5c59d9f0e18f834c52fc1083"
COINS_E_SECRET = "dcece69ba87d48e2295f3ca593e6ee05f655c27a4b831a0dd631b9dc355329e0" # this has been reset already

BASE_API_URL = "https://www.coins-e.com/api/v2"


print "Coins-E Trade API access test" 
print "Get your API keys from https://www.coins-e.com/exchange/api/access/" 



def unauthenticated_request(url_suffix):
    url_request_object = urllib2.Request("%s/%s" % (BASE_API_URL,url_suffix))
    response = urllib2.urlopen(url_request_object)    
    response_json = {}
    try:
        response_content = response.read()
        response_json = json.loads(response_content)        
        return response_json
    finally:
        response.close()
    return "failed"
    


def authenticated_request(url_suffix, method, post_args={}):
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
    required_sign = hmac.new(COINS_E_SECRET, post_data, hashlib.sha512).hexdigest()
    headers = {}
    headers['key'] = COINS_E_API_KEY
    headers['sign'] = required_sign
    url_request_object = urllib2.Request("%s/%s" % (BASE_API_URL,url_suffix),
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



#unauthenticated requests
#List of all markets and the status
market_list_request = unauthenticated_request('markets/list/')
print market_list_request

#List of all coins and the status
coin_list_request = unauthenticated_request('coins/list/')
print coin_list_request

#get consolidated market data
consolidate_market_data_request = unauthenticated_request('markets/data/')
print consolidate_market_data_request

    
#authenticated requests
user_all_wallets = authenticated_request('wallet/all/',"getwallets")
print user_all_wallets['wallets']
    
    
working_pair = "WDC_BTC"

#placing a new order    
new_order_request = authenticated_request('market/%s/' % (working_pair),"neworder",{'order_type':'buy',
                                                                                         'rate':'0.002123',
                                                                                         'quantity':'1',})
print new_order_request

# #get information about an order
# get_order_request = authenticated_request('market/%s/' % (working_pair),"getorder",{'order_id':new_order_request['order']['id']})
# print get_order_request
                                          
# #get list of orders
# get_list_of_order_request = authenticated_request('market/%s/' % (working_pair),"listorders",{'limit':2})

# print get_list_of_order_request

# for each_order in get_list_of_order_request['orders']:
#     print each_order['status']


# #cancel an order
# order_cancel_request = authenticated_request('market/%s/' % (working_pair),"cancelorder",{'order_id':get_order_request['order']['id']})
# print order_cancel_request
