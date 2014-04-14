# implements API access to CryptoStocks.com
# not a conventional bitcoin exchange but has basically
# the same API functions

from Exchange import Exchange
from order import Order

class CryptoStocks(Exchange):
    def __init__(self, api_key, secret):
        self.api = Cryptsy_api(api_key, secret)
        super(Cryptsy, self).__init__()
        self.name = 'CRYPTSY'
        self.trading_fee = 0.003# 0.2% to buy and 0.3% to sell. Those bastards!
        self.marketids = {}

    def get_tradeable_pairs(self):
        tradeable_pairs = []
        self.market_ids = {}
        data = self.api.getMarketDataV2()
        if data is None:
            # try again
            print('retrying Cryptsy request...')
            return self.get_tradeable_pairs()
        else:
            for market in data['return']['markets'].values():
                base = market['primarycode']
                alt = market['secondarycode']
                tradeable_pairs.append((base, alt))
                # while we're doing this, also
                # initialize the maps to marketids
                slug = base + "_" + alt
                self.market_ids[slug] = market['marketid']
            return tradeable_pairs

    def get_min_vol(self, pair, depth):
        '''
        Mar 21 2014 - Cryptsy changes minimum order volume to 0.0000001
        '''
        base, alt = pair
        slug = base + "_" + alt
        test = self.get_validated_pair(pair)
        if test is not None:
            true_pair, swapped = test
            if not swapped:
                return 0.0000001
            else:
                # we need to use the depth information to calculate
                # how much alt we need to trade to fulfill min base vol
                return self.get_clipped_alt_volume(depth, 0.0000001)

    def get_highest_bid(self, base, alt):
        # RETURNS PRICE in units of ALT!
        pair0 = (base, alt)
        pair, swapped = self.get_validated_pair(pair0)
        newbase, newalt = pair
        marketid = self.get_market_id(newbase, newalt)
        data = self.api.getOrderbookData(marketid)['return'][newbase]

        if swapped:
            # we are interested in sell orders instead of buy orders
            bidprice = float(data['sellorders'][0]['price'])
            bidprice = 1.0/bidprice
        else:
            # first one is the best offer
            bidprice = float(data['buyorders'][0]['price'])

        return bidprice

    def get_lowest_ask(self, base, alt):
        pair0 = (base, alt)
        pair, swapped = self.get_validated_pair(pair0)
        newbase, newalt = pair
        marketid = self.get_market_id(newbase, newalt)
        data = self.api.getOrderbookData(marketid)['return'][newbase]
        if swapped:
            askprice = float(data['buyorders'][0]['price'])
            askprice = 1.0/askprice
        else:
            askprice = float(data['sellorders'][0]['price'])

        return askprice

    def get_depth(self, base, alt):
        pair0 = (base, alt)
        pair, swapped = self.get_validated_pair(pair0)
        newbase, newalt = pair
        marketid = self.get_market_id(newbase, newalt)
        data = self.api.depth(marketid)['return']
        book = { "bids" : [], "asks" : [] }
        if swapped:
            for bid in data['buy']:
                # find out
                o = Order(float(bid[0]),float(bid[1]))
                ask = get_swapped_order(o)
                book['asks'].append(ask)
            for ask in data['sell']:
                o = Order(float(ask[0]), float(ask[1]))
                bid = get_swapped_order(o)
                book['bids'].append(bid)
        else:
            for bid in data['buy']:
                o = Order(float(bid[0]),float(bid[1]))
                book['bids'].append(o)
            for ask in data['sell']:
                o = Order(float(ask[0]), float(ask[1]))
                book['asks'].append(o)
        return book

    def get_balance(self, currency):
        balances = self.api.getInfo()['return']['balances_available']
        return float(balances.get(currency, 0.0))

    def get_all_balances(self):
        data = self.api.getInfo()
        balances = {k:float(v) for k,v in data['return']['balances_available'].items()}
        return balances

    def submit_order(self, gc, gv, rc, rv):
        pair0 = (gc, rc)
        pair, swapped = self.get_validated_pair(pair0)
        marketid = self.get_market_id(pair)

        if swapped:
            ordertype = "Buy"
            quantity = rv
            price = gv/rv
        else:
            ordertype = "Sell"
            quantity = gv
            price = rv/gv
        self.api.createOrder(marketid, ordertype, quantity, price)

    def confirm_order(self, orderID):
        data = self.api.allMyOrders()
        #data is all my open orders so check to see if orderID is no longer in there
        return NotImplemented

    # CRYPTSY-specific
    def get_market_id(self, base, alt):
        if (base, alt) in self.tradeable_pairs:
            slug = base + "_" + alt
            return self.market_ids[slug]
        elif (alt, base) in self.tradeable_pairs:
            slug = alt + "_" + base
            return self.market_ids[slug]
        else:
            return 'ERROR!'

#     def validate_data(self, data):
#         if data['success'] != 1:
#             DONT WORK ON THIS NPW
