from Exchange import Exchange
import bterapi
import os
from order import Order

class BTER(Exchange):
    def __init__(self, keyfile):
        keyfile = os.path.abspath(keyfile)
        self.keyhandler = bterapi.KeyHandler(keyfile)
        key = self.keyhandler.getKeys()[0]
        self.conn = bterapi.BTERConnection()
        self.api = bterapi.TradeAPI(key, self.keyhandler)
        super(BTER, self).__init__()
        self.name = 'BTER'
        self.trading_fee = 0.002

    def get_tradeable_pairs(self):
        tradeable_pairs = []
        for pair in bterapi.all_pairs:
            a, b = pair.split("_")
            tradeable_pairs.append((a.upper(), b.upper()))
        return tradeable_pairs

    def get_depth(self, base, alt):
        book = {'bids': [], 'asks': []}
        pair, swapped = self.get_validated_pair((base, alt))
        if pair is None:
            return

        pairstr = pair[0].lower() + "_" + pair[1].lower()
        asks, bids = bterapi.getDepth(pairstr)

        book['bids'] = [Order(float(b[0]), float(b[1])) for b in bids]
        book['asks'] = [Order(float(a[0]), float(a[1])) for a in asks]

        return book

    def get_balance(self, currency):
        funds = self.api.getFunds(self.conn, error_handler=None)
        if currency in funds:
            return float(funds[currency])
        else:
            return 0.0
        # data = self.api.getInfo(connection = self.conn)
        #return getattr(data, 'balance_' + currency.lower())

    def get_all_balances(self):
        funds = self.api.getFunds(self.conn, error_handler=None)
        return {k:float(v) for k,v in funds.items()}

    def submit_order(self, gc, gv, rc, rv):
        return NotImplemented
#         pair, swapped = self.get_validated_pair((rc, gc))
#         print swapped
#         if pair is None:
#             return
#         pairstr = pair[0].lower() + "_" + pair[1].lower()
#         if swapped:
#             price = rv/gv
#             self.api.trade(pairstr, 'sell', price, gv)
#         else:
#             price = gv/rv
#             self.api.trade(pairstr, 'buy', price, rv)

    def confirm_order(self, orderID):
        pass



# from Exchange import Exchange
# from PairList import PairList
# import bterapi
#
# class BTER(Exchange):
#     """docstring for BTER"""
#     def __init__(self, mode, keyfile):
#         super(BTER, self).__init__(mode)
#         self.name = 'BTER'
#         self.full_orderbook = False
#         self.trading_fee = 0.002
#         # bterapi already kindly provides us with a list of supported pairs
#         for pair in bterapi.all_pairs:
#             a, b = pair.split("_")
#             self.supported_pairs.add_pair((a.upper(), b.upper()))
#         # set up API
#         self.keyhandler = bterapi.KeyHandler(keyfile)
#         key = self.keyhandler.getKeys()[0]
#         self.conn = bterapi.BTERConnection()
#         self.api = bterapi.TradeAPI(key, self.keyhandler)
#
#     def live_order(self, recv_currency, recv_volume, give_currency, give_volume):
#
#         return NotImplemented
#
#     def update_live_balance(self, currency=None):
#         data = self.api.getFunds(self.conn, error_handler=None)
#         foo = 1
#         return NotImplemented
#
#     def update_orders(self, pair):
#         a, b = pair
#         pairstr = a.lower() + "_" + b.lower()
#         pairstr, flipped = self.check_swapped(pairstr)
#         if flipped:
#             alt, base = pair
#         else:
#             base, alt = pair
#         # base, alt not necessarily the same as one dictated in ArbitrageBot class
#         asks, bids = bterapi.getDepth(pairstr)
#         for bid in bids:
#             rate = float(bid[0])
#             give_vol = float(bid[1])
#             recv_vol = give_vol * rate
#             order = {"give_currency" : base, \
#                      "recv_currency" : alt, \
#                      "give_volume" : give_vol, \
#                      "recv_volume" : recv_vol }
#             self.orderbook.set_order(order)
#         for ask in asks:
#             rate = float(ask[0])
#             recv_vol = float(ask[1])
#             give_vol = recv_vol * rate
#             order = {"give_currency" : alt, \
#                      "recv_currency" : base, \
#                      "give_volume" : give_vol, \
#                      "recv_volume" : recv_vol }
#             self.orderbook.set_order(order)
#
#
#     def check_swapped(self, pairstr):
#         '''
#         returns swapped_pair, True if pair has been swapped
#         else returns pairstr, False
#         '''
#         if pairstr not in bterapi.all_pairs:
#             if "_" in pairstr:
#                 a, b = pairstr.split("_")
#                 swapped_pair = "%s_%s" % (b.lower(), a.lower())
#                 if swapped_pair in bterapi.all_pairs:
#                     return swapped_pair, True
#             msg = "unrecognized pair " + pairstr
#             raise Exception(msg)
#         return pairstr, False