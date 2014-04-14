# Copyright (c) 2013 Alan McIntyre

import urllib
import hashlib
import hmac
import warnings
from datetime import datetime

from btceapi import common
from btceapi import keyhandler


class InvalidNonceException(Exception):
    def __init__(self, method, expectedNonce, actualNonce):
        Exception.__init__(self)
        self.method = method
        self.expectedNonce = expectedNonce
        self.actualNonce = actualNonce

    def __str__(self):
        return "Expected a nonce greater than %d" % self.expectedNonce


class TradeAccountInfo(object):
    '''An instance of this class will be returned by
    a successful call to TradeAPI.getInfo.'''

    def __init__(self, info):
        funds = info.get(u'funds')
        for c in common.all_currencies:
            setattr(self, "balance_%s" % c, funds.get(unicode(c), 0))

        self.open_orders = info.get(u'open_orders')
        self.server_time = datetime.fromtimestamp(info.get(u'server_time'))

        self.transaction_count = info.get(u'transaction_count')
        rights = info.get(u'rights')
        self.info_rights = (rights.get(u'info') == 1)
        self.withdraw_rights = (rights.get(u'withdraw') == 1)
        self.trade_rights = (rights.get(u'trade') == 1)


class TransactionHistoryItem(object):
    '''A list of instances of this class will be returned by
    a successful call to TradeAPI.transHistory.'''

    def __init__(self, transaction_id, info):
        self.transaction_id = transaction_id
        items = ("type", "amount", "currency", "desc",
                 "status", "timestamp")
        for n in items:
            setattr(self, n, info.get(n))
        self.timestamp = datetime.fromtimestamp(self.timestamp)


class TradeHistoryItem(object):
    '''A list of instances of this class will be returned by
    a successful call to TradeAPI.tradeHistory.'''

    def __init__(self, transaction_id, info):
        self.transaction_id = transaction_id
        items = ("pair", "type", "amount", "rate", "order_id",
                 "is_your_order", "timestamp")
        for n in items:
            setattr(self, n, info.get(n))
        self.timestamp = datetime.fromtimestamp(self.timestamp)


class OrderItem(object):
    '''A list of instances of this class will be returned by
    a successful call to TradeAPI.activeOrders.'''

    def __init__(self, order_id, info):
        self.order_id = int(order_id)
        vnames = ("pair", "type", "amount", "rate", "timestamp_created",
                  "status")
        for n in vnames:
            setattr(self, n, info.get(n))
        self.timestamp_created = datetime.fromtimestamp(self.timestamp_created)


class TradeResult(object):
    '''An instance of this class will be returned by
    a successful call to TradeAPI.trade.'''

    def __init__(self, info):
        self.received = info.get(u"received")
        self.remains = info.get(u"remains")
        self.order_id = info.get(u"order_id")
        funds = info.get(u'funds')
        for c in common.all_currencies:
            setattr(self, "balance_%s" % c, funds.get(unicode(c), 0))


class CancelOrderResult(object):
    '''An instance of this class will be returned by
    a successful call to TradeAPI.cancelOrder.'''

    def __init__(self, info):
        self.order_id = info.get(u"order_id")
        funds = info.get(u'funds')
        for c in common.all_currencies:
            setattr(self, "balance_%s" % c, funds.get(unicode(c), 0))


def setHistoryParams(params, from_number, count_number, from_id, end_id,
                     order, since, end):
    if from_number is not None:
        params["from"] = "%d" % from_number
    if count_number is not None:
        params["count"] = "%d" % count_number
    if from_id is not None:
        params["from_id"] = "%d" % from_id
    if end_id is not None:
        params["end_id"] = "%d" % end_id
    if order is not None:
        if order not in ("ASC", "DESC"):
            raise Exception("Unexpected order parameter: %r" % order)
        params["order"] = order
    if since is not None:
        params["since"] = "%d" % since
    if end is not None:
        params["end"] = "%d" % end


class TradeAPI(object):
    def __init__(self, key, handler):
        self.key = key
        self.handler = handler

        if not isinstance(self.handler, keyhandler.KeyHandler):
            raise Exception("The handler argument must be a"
                            " keyhandler.KeyHandler")

        # We depend on the key handler for the secret
        self.secret = handler.getSecret(key)

    def _post(self, params, connection=None, raiseIfInvalidNonce=False):
        params["nonce"] = self.handler.getNextNonce(self.key)
        encoded_params = urllib.urlencode(params)

        # Hash the params string to produce the Sign header value
        H = hmac.new(self.secret, digestmod=hashlib.sha512)
        H.update(encoded_params)
        sign = H.hexdigest()

        if connection is None:
            connection = common.BTCEConnection()

        headers = {"Key": self.key, "Sign": sign}
        result = connection.makeJSONRequest("/tapi", headers, encoded_params)

        success = result.get(u'success')
        if not success:
            err_message = result.get(u'error')
            method = params.get("method", "[uknown method]")

            if "invalid nonce" in err_message:
                # If the nonce is out of sync, make one attempt to update to
                # the correct nonce.  This sometimes happens if a bot crashes
                # and the nonce file doesn't get saved, so it's reasonable to
                # attempt one correction.  If multiple threads/processes are
                # attempting to use the same key, this mechanism will
                # eventually fail and the InvalidNonce will be emitted so that
                # you'll end up here reading this comment. :)

                # The assumption is that the invalid nonce message looks like
                # "invalid nonce parameter; on key:4, you sent:3"
                s = err_message.split(",")
                expected = int(s[-2].split(":")[1])
                actual = int(s[-1].split(":")[1])
                if raiseIfInvalidNonce:
                    raise InvalidNonceException(method, expected, actual)

                warnings.warn("The nonce in the key file is out of date;"
                              " attempting to correct.")
                self.handler.setNextNonce(self.key, expected + 1)
                return self._post(params, connection, True)
            elif "no orders" in err_message and method == "ActiveOrders":
                # ActiveOrders returns failure if there are no orders;
                # intercept this and return an empty dict.
                return {}

            raise Exception("%s call failed with error: %s"
                            % (method, err_message))

        if u'return' not in result:
            raise Exception("Response does not contain a 'return' item.")

        return result.get(u'return')

    def getInfo(self, connection=None):
        params = {"method": "getInfo"}
        return TradeAccountInfo(self._post(params, connection))

    # custom mod function
    def getBalances(self, connection=None):
        params ={"method":"getInfo"}
        info = self._post(params, connection)
        funds = info.get(u'funds')
        balances = {}
        for c in common.all_currencies:
            balances[c.upper()] = float(funds.get(unicode(c), 0))
        return balances

    def transHistory(self, from_number=None, count_number=None,
                     from_id=None, end_id=None, order="DESC",
                     since=None, end=None, connection=None):

        params = {"method": "TransHistory"}

        setHistoryParams(params, from_number, count_number, from_id, end_id,
                         order, since, end)

        orders = self._post(params, connection)
        result = []
        for k, v in orders.items():
            result.append(TransactionHistoryItem(int(k), v))

        # We have to sort items here because the API returns a dict
        if "ASC" == order:
            result.sort(key=lambda a: a.transaction_id, reverse=False)
        elif "DESC" == order:
            result.sort(key=lambda a: a.transaction_id, reverse=True)

        return result

    def tradeHistory(self, from_number=None, count_number=None,
                     from_id=None, end_id=None, order=None,
                     since=None, end=None, pair=None, connection=None):

        params = {"method": "TradeHistory"}

        setHistoryParams(params, from_number, count_number, from_id, end_id,
                         order, since, end)

        if pair is not None:
            common.validatePair(pair)
            params["pair"] = pair

        orders = self._post(params, connection)
        result = []
        for k, v in orders.items():
            result.append(TradeHistoryItem(k, v))

        return result

    def activeOrders(self, pair=None, connection=None):

        params = {"method": "ActiveOrders"}

        if pair is not None:
            common.validatePair(pair)
            params["pair"] = pair

        orders = self._post(params, connection)
        result = []
        for k, v in orders.items():
            result.append(OrderItem(k, v))

        return result

    def trade(self, pair, trade_type, rate, amount, connection=None):
        common.validateOrder(pair, trade_type, rate, amount)
        params = {"method": "Trade",
                  "pair": pair,
                  "type": trade_type,
                  "rate": common.formatCurrency(rate, pair),
                  "amount": common.formatCurrency(amount, pair)}

        return TradeResult(self._post(params, connection))

    def cancelOrder(self, order_id, connection=None):
        params = {"method": "CancelOrder",
                  "order_id": order_id}
        return CancelOrderResult(self._post(params, connection))