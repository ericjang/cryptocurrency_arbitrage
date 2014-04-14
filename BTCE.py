from Exchange import Exchange
import btceapi
import os
from order import Order

class BTCE(Exchange):
    def __init__(self, keyfile):
        keyfile = os.path.abspath(keyfile)
        self.keyhandler = btceapi.KeyHandler(keyfile)
        key = self.keyhandler.getKeys()[0]
        self.conn = btceapi.BTCEConnection()
        self.api = btceapi.TradeAPI(key, self.keyhandler)
        super(BTCE, self).__init__()
        self.name = 'BTCE'
        self.trading_fee = 0.002

    def get_tradeable_pairs(self):
        tradeable_pairs = []
        for pair in btceapi.all_pairs:
            a, b = pair.split("_")
            tradeable_pairs.append((a.upper(), b.upper()))
        return tradeable_pairs

    def get_depth(self, base, alt):
        book = {'bids': [], 'asks': []}
        pair, swapped = self.get_validated_pair((base, alt))
        if pair is None:
            return

        pairstr = pair[0].lower() + "_" + pair[1].lower()
        if swapped:
            bids, asks = btceapi.getDepth(pairstr)
        else:
            asks, bids = btceapi.getDepth(pairstr)

        book['bids'] = [Order(float(b[0]), float(b[1])) for b in bids]
        book['asks'] = [Order(float(a[0]), float(a[1])) for a in asks]

        return book

    def get_balance(self, currency):
        data = self.api.getInfo(connection = self.conn)
        return getattr(data, 'balance_' + currency.lower())

    def get_all_balances(self):
        balances = self.api.getBalances(self.conn)
        return balances

    def submit_order(self, gc, gv, rc, rv):
        pair, swapped = self.get_validated_pair((rc, gc))
        print swapped
        if pair is None:
            return
        pairstr = pair[0].lower() + "_" + pair[1].lower()
        if swapped:
            price = rv/gv
            self.api.trade(pairstr, 'sell', price, gv)
        else:
            price = gv/rv
            self.api.trade(pairstr, 'buy', price, rv)

    def confirm_order(self, orderID):
        pass

#     def get_min_vol(self, base, alt):
#         '''
#         returns the minimum required trading volume for the currency
#         (buy and sell orders)
#         '''
#         for slug in btceapi.min_orders:
#             b = slug.split("_")[0].upper()
#             if b == base:
#                 return float(btceapi.min_orders[slug])
#         return 0.1

    def get_min_vol(self, pair, depth):
        """
        override default implementation - BTCE has min volumes 0.1 ALT !!!
        """
        base, alt = pair
        slug = base + "_" + alt
        test = self.get_validated_pair(pair)
        if test is not None:
            true_pair, swapped = test
            if not swapped:
                return 0.1
            else:
                # we need to use the depth information to calculate
                # how much alt we need to trade to fulfill min base vol
                return self.get_clipped_alt_volume(depth, 0.101)