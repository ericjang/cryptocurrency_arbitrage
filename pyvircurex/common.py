import time
import json
import urllib
import httplib
import hashlib


#domain = "vircurex.com" <- deprecated Jan 31
# UPDATE JAN 12 : new api domain api.vircurex.com
domain = "api.vircurex.com"

api_schema = {
    "lowest_ask" : {
        "url" : "/api/get_lowest_ask.json",
        "return" : "value",
        "type" : float
    },
    "highest_bid" : {
        "url" : "/api/get_highest_bid.json",
        "return" : "value",
        "type" : float
    },
    "last_trade" : {
        "url" : "/api/get_last_trade.json",
        "return" : "value",
        "type" : float
    },
    "volume" : {
        "url" : "/api/get_volume.json",
        "return" : "value",
        "type" : float
    },
    "info" : {
        "url" : "/api/get_info_for_currency.json",
        "type" : dict
    },
    "currentcy_info" : {
        "url" : "/api/get_info_for_1_currency.json",
        "type" : dict
    },
    "orderbook" : {
        "url" : "/api/orderbook.json",
        "type" : dict
    },
    "trades" : {
        "url" : "/api/trades.json",
        "type" : list
    },
    "balance" : {
        "url" : "/api/get_balance.json",
        "return" : "balance",
        "type" : float,
        "token" : {
            # secret;user;timestamp;ID;get_balance;currency
            "input" : "%s;%s;%s;%i;get_balance;%s",
            # secret;user;timestamp;get_balance;balance
            "output" : "%s;%s;%s;get_balance;%s"
        }
    },
    "balances" : {
        "url" : "/api/get_balances.json",
        "return" : "balances",
        "type" : dict,
        "token" : {
            # secret;user;timestamp;ID;get_balance
            "input" : "%s;%s;%s;%i;get_balances",
            # secret;user;timestamp;get_balance;balance
            "output" : "%s;%s;%s;get_balances;%s"
        }
    },
    "order" : {
        "url" : "/api/read_order.json",
        "type" : dict,
        "token" : {
            # secret;user;timestamp;ID;read_order;orderid
            "input" : "%s;%s;%s;%i;read_order;%i",
            # secret;user;timestamp;get_balance;read_order;orderid
            "output" : "%s;%s;%s;read_order;%i"
        }
    },
    "orders" : {
        "url" : "/api/read_orders.json",
        "type" : dict,
        "token" : {
            # secret;user;timestamp;ID;read_orders
            "input" : "%s;%s;%s;%i;read_orders",
            # secret;user;timestamp;read_order
            "output" : "%s;%s;%s;read_orders"
        }
    },
    "create_order" : {
        "url" : "/api/create_order.json",
        "type" : dict,
        "token" : {
            # secret;user;timestamp;ID;create_order;ordertype;amount;base;unitprice;alternate
            "input" : "%s;%s;%s;%i;create_order;%s;%s;%s;%s;%s",
            # secret;user;timestamp;create_order;orderid
            "output" : "%s;%s;%s;read_orders;%s"
        }
    },
    "create_released_order" : {
        "url" : "/api/create_released_order.json",
        "type" : dict,
        "token" : {
            # secret;user;timestamp;ID;create_order;ordertype;amount;base;unitprice;alternate
            "input" : "%s;%s;%s;%i;create_order;%s;%s;%s;%s;%s",
            # secret;user;timestamp;create_order;orderid
            "output" : "%s;%s;%s;read_orders;%s"
        }
    },
    "delete_order" : {
        "url" : "/api/delete_order.json",
        "type" : dict,
        "token" : {
            # secret;user;timestamp;ID;delete_order;orderid
            "input" : "%s;%s;%s;%i;delete_order;%i",
            # secret;user;timestamp;delete_order;orderid
            "output" : "%s;%s;%s;delete_order;%i"
        }
    },
    "release_order" : {
        "url" : "/api/release_order.json",
        "type" : dict,
        "token" : {
            # secret;user;timestamp;ID;release_order;orderid
            "input" : "%s;%s;%s;%i;release_order;%i",
            # secret;user;timestamp;release_order;orderid
            "output" : "%s;%s;%s;release_order;%i"
        }
    },
}


def request(api, params):
    params = urllib.urlencode(params)
    url = "%s?%s" % (api["url"], params)

    connection = httplib.HTTPSConnection(domain)
    connection.request("GET", url, {}, {})
    response = connection.getresponse().read()
    connection.close()

    return json.loads(response)


def public_request(api_call, params={}):
    api = api_schema[api_call]
    data = request(api, params)

    if api.has_key("return"):
        return api["type"](data[api["return"]])

    return data


def secure_request(account, api_call, names=(), params=(), otherparams={}):
    api = api_schema[api_call]

    stamp, token = make_token(account, api["token"]["input"], params)
    request_params = {
        "account" : account.user,
        "id" : account.tid,
        "token" : token,
        "timestamp" : stamp,
    }
    request_params.update(zip(names, params))
    request_params.update(otherparams)

    data = request(api, request_params)

    #print data
    #print api
    if api.has_key("return"):
        value = data[api["return"]]
    else:
        value = data

    account.tid += 1
    return api["type"](value)


def make_token(account, token_string, params):
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S", tuple(time.gmtime()))
    params = tuple([account.secret, account.user, stamp, account.tid] + list(params))

    token = hashlib.sha256(token_string % params).hexdigest()
    return stamp, token


def check_token(account, stamp, token_string, params):
    params = tuple([account.secret, account.user, stamp] + list(params))

    token = hashlib.sha256(token_string % params).hexdigest()
    return  token

