# Copyright (c) 2013 Alan McIntyre

import datetime
import decimal

from btceapi import common


def getTradeFee(pair, connection=None):
    '''
    Retrieve the fee (in percent) associated with trades for a given pair.
    '''

    common.validatePair(pair)

    if connection is None:
        connection = common.BTCEConnection()

    fees = connection.makeJSONRequest("/api/2/%s/fee" % pair)
    if type(fees) is not dict:
        raise Exception("The response is not a dict.")

    trade_fee = fees.get(u'trade')
    if type(trade_fee) is not decimal.Decimal:
        raise Exception("The response does not contain a trade fee")

    return trade_fee


class Ticker(object):
    __slots__ = ('high', 'low', 'avg', 'vol', 'vol_cur', 'last', 'buy', 'sell',
                 'updated', 'server_time')

    def __init__(self, **kwargs):
        for s in Ticker.__slots__:
            setattr(self, s, kwargs.get(s))

        self.updated = datetime.datetime.fromtimestamp(self.updated)
        self.server_time = datetime.datetime.fromtimestamp(self.server_time)

    def __getstate__(self):
        return dict((k, getattr(self, k)) for k in Ticker.__slots__)

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)


def getTicker(pair, connection=None):
    '''Retrieve the ticker for the given pair.  Returns a Ticker instance.'''

    common.validatePair(pair)

    if connection is None:
        connection = common.BTCEConnection()

    response = connection.makeJSONRequest("/api/2/%s/ticker" % pair)

    if type(response) is not dict:
        raise Exception("The response is a %r, not a dict." % type(response))

    return Ticker(**response[u'ticker'])


def getDepth(pair, connection=None):
    '''Retrieve the depth for the given pair.  Returns a tuple (asks, bids);
    each of these is a list of (price, volume) tuples.'''

    common.validatePair(pair)

    if connection is None:
        connection = common.BTCEConnection()

    depth = connection.makeJSONRequest("/api/2/%s/depth" % pair)
    if type(depth) is not dict:
        raise Exception("The response is not a dict.")

    asks = depth.get(u'asks')
    if type(asks) is not list:
        raise Exception("The response does not contain an asks list.")

    bids = depth.get(u'bids')
    if type(bids) is not list:
        raise Exception("The response does not contain a bids list.")

    return asks, bids


class Trade(object):
    __slots__ = ('pair', 'trade_type', 'price', 'tid', 'amount', 'date')

    def __init__(self, **kwargs):
        for s in Trade.__slots__:
            setattr(self, s, kwargs.get(s))

        if type(self.date) in (int, float, decimal.Decimal):
            self.date = datetime.datetime.fromtimestamp(self.date)
        elif type(self.date) in (str, unicode):
            if "." in self.date:
                self.date = datetime.datetime.strptime(self.date,
                                                       "%Y-%m-%d %H:%M:%S.%f")
            else:
                self.date = datetime.datetime.strptime(self.date,
                                                       "%Y-%m-%d %H:%M:%S")

    def __getstate__(self):
        return dict((k, getattr(self, k)) for k in Trade.__slots__)

    def __setstate__(self, state):
        for k, v in state.items():
            setattr(self, k, v)


def getTradeHistory(pair, connection=None, count=None):
    '''Retrieve the trade history for the given pair.  Returns a list of
    Trade instances.  If count is not None, it should be an integer, and
    specifies the number of items from the trade history that will be
    processed and returned.'''

    common.validatePair(pair)

    if connection is None:
        connection = common.BTCEConnection()

    history = connection.makeJSONRequest("/api/2/%s/trades" % pair)

    if type(history) is not list:
        raise Exception("The response is a %r, not a list." % type(history))

    result = []

    # Limit the number of items returned if requested.
    if count is not None:
        history = history[:count]

    for h in history:
        h["pair"] = pair
        t = Trade(**h)
        result.append(t)
    return result