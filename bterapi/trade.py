# Copyright (c) 2013 Alan McIntyre

import urllib
import hashlib
import hmac
from datetime import datetime
import decimal
import time

import common
import keyhandler


# Putting this here in case I change my mind and want to use UTC or something.
def now():
    return datetime.now()


def validate_order(func):
    def validated_func(order, *args, **kwargs):
        if type(order) is OrderItem:
            order = order.order_id
        return func(order, *args, **kwargs)
    return validated_func


class OrderItem(object):
    """
    An instance of this class will be returned by successful calls to TradeAPI.getOrderStatus and TradeAPI.placeOrder.
    """
    def __init__(self, order_id, info=None, initial_params=None, date=None):
        self.order_id = int(order_id)
        if info is not None:
            order = info.get(u'order')
            if type(order) is not dict:
                raise Exception('The response is a %r, not a dict.' % type(order))
            self.status = order[u'status']
            self.pair = order[u'pair']
            self.type = order[u'type']
            self.rate = decimal.Decimal(order[u'rate'])
            self.amount = decimal.Decimal(order[u'amount'])
            self.initial_rate = decimal.Decimal(order[u'initial_rate'])
            self.initial_amount = decimal.Decimal(order[u'initial_amount'])
        else:
            self.status = None
            if initial_params is not None:
                self.pair = initial_params['pair']
                self.type = initial_params['type']
                self.rate = initial_params['rate']
                self.amount = initial_params['amount']
                self.initial_rate = initial_params['rate']
                self.initial_amount = initial_params['amount']
            else:
                self.initial_rate = None
                self.initial_amount = None

        if date is not None:
            self.date = date
        elif not hasattr(self, 'date'):
            self.date = None


class TradeAPI(object):
    def __init__(self, key, handler):
        self.key = key
        self.handler = handler

        if type(self.handler) is not keyhandler.KeyHandler:
            raise Exception("The handler argument must be a keyhandler.KeyHandler")

        # We depend on the key handler for the secret
        self.secret = handler.getSecret(key)

    def _post(self, api_method, params=None, connection=None, error_handler=None):
        if params is None:
            params = {'nonce': datetime.now().microsecond}
        else:
            params["nonce"] = datetime.now().microsecond
        encoded_params = urllib.urlencode(params)

        # Hash the params string to produce the Sign header value
        H = hmac.new(self.secret, digestmod=hashlib.sha512)
        H.update(encoded_params)
        sign = H.hexdigest()

        if connection is None:
            connection = common.BTERConnection()

        headers = {"Key": self.key, "Sign": sign}
        result = connection.makeJSONRequest('/api/1/private/' + api_method, method='POST',
                                            extra_headers=headers, params=encoded_params)

        return common.validateResponse(result, error_handler=error_handler)

    def getFunds(self, connection=None, error_handler=None):
        '''
        modified this
        '''
#         info = self._post('getfunds', connection=connection, error_handler=error_handler)
#         balances = {c: {'available': decimal.Decimal(0), 'locked': decimal.Decimal(0)}
#                     for c in common.all_currencies}
#         if info.get(u'available_funds') is not None:
#             for c, v in info.get(u'available_funds').items():
#                 balances[c.lower()]['available'] = decimal.Decimal(v)
#         if info.get(u'locked_funds') is not None:
#             for c, v in info.get(u'locked_funds').items():
#                 balances[c.lower()]['locked'] = decimal.Decimal(v)
#
#         return balances
        info = self._post('getfunds', connection=connection, error_handler=error_handler)
        return info.get(u'available_funds', {}) # empty dict if no funds at all

    @validate_order
    def getOrderStatus(self, order_id, connection=None, error_handler=None):
        result = self._post('getorder', params={'order_id': order_id},
                            connection=connection, error_handler=error_handler)
        return OrderItem(order_id, result)

    def placeOrder(self, pair, trade_type, rate, amount, connection=None, update_delay=None, error_handler=None):
        common.validatePair(pair)
        if trade_type.lower() not in ("buy", "sell"):
            if trade_type.lower() == 'bid':
                trade_type = 'buy'
            elif trade_type.lower() == 'ask':
                trade_type = 'sell'
            else:
                raise Exception("Unrecognized trade type: %r" % trade_type)

        params = {"pair": pair,
                  "type": trade_type.upper(),
                  "rate": common.formatCurrency(rate, pair, 'price'),
                  "amount": common.formatCurrency(amount, pair, 'amount')}

        order = OrderItem(self._post('placeorder', params=params, connection=connection,
                                     error_handler=error_handler).get(u'order_id'), initial_params=params, date=now())

        if update_delay is not None:
            time.sleep(update_delay)
            order = self.getOrderStatus(order.order_id, connection=None)

        return order

    @validate_order
    def cancelOrder(self, order_id, connection=None, error_handler=None):
        result = self._post('cancelorder', params={'order_id': order_id}, connection=connection,
                            error_handler=error_handler)
        return result.get('msg')