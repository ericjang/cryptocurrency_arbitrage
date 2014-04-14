from Exchange import Exchange
from crypto_trade import CryptoTradeAPI
from myutils import get_swapped_order
from order import Order

class CryptoTrade(Exchange):
    def __init__(self, api_key, secret):
        self.api = CryptoTradeAPI(api_key, secret)
        super(CryptoTrade, self).__init__()
        self.name = 'CRYPTO-TRADE'
        self.trading_fee = 0.002

    def get_tradeable_pairs(self):
        return [('BTC','USD'), ('BTC','EUR'), ('LTC','USD'), ('LTC','BTC'), ('NMC','USD'),
                ('NMC','BTC'), ('XPM','USD'), ('XPM','BTC'), ('XPM','PPC'), ('PPC','USD'),
                ('PPC','BTC'), ('TRC','BTC'), ('FTC','USD'), ('FTC','BTC'), ('DVC','BTC'),
                ('WDC','USD'), ('WDC','BTC'), ('DGC', 'BTC')]

    def get_depth(self, base, alt):
        book = {'bids': [], 'asks': []}
        pair, swapped = self.get_validated_pair((base, alt))
        b,a = pair
        slug = b.lower() + "_" + a.lower()
        data = self.api.reqpublic('depth' + '/' + slug)
        if swapped:
            for ask in data['asks']:
                o = Order(float(ask[0]), float(ask[1]))
                bid = get_swapped_order(o)
                book['bids'].append(bid)
            for bid in data['bids']:
                o = Order(float(bid[0]), float(bid[1]))
                ask = get_swapped_order(o)
                book['asks'].append(ask)
        else:
            for bid in data['bids']:
                o = Order(float(bid[0]), float(bid[1]))
                book['bids'].append(o)
            for ask in data['asks']:
                o = Order(float(ask[0]), float(ask[1]))
                book['asks'].append(o)
        return book

    def get_balance(self, currency):
        funds = self.api.req('getinfo')['data']['funds']
        return float(funds.get(currency.lower(), 0.0))

    def get_all_balances(self):
        funds = self.api.req('getinfo')['data']['funds']
        balances = {k.upper() : float(v) for k,v in funds.items()}
        return balances

    def submit_order(self, gc, gv, rc, rv):
        return NotImplemented

    def confirm_order(self, orderID):
        return NotImplemented




# cryp.req('trade',{"pair":"ltc_btc","type":"Buy","amount":ltc_bid_amount,"rate":price_to_bid})
#
# #Example Cancelling an order
# cryp.req('cancelorder',{"orderid":order_id})
#
# #Example Get Funds
# account_info=cryp.req('getinfo')
#
# orig_crypto_ltc_amount=float(account_info['data']['funds']['ltc'])



# from Exchange import Exchange
# from crypto_trade import CryptoTrade as API
#
# class CryptoTrade(Exchange):
#     def __init__(self, mode, api_key, secret):
#         super(CryptoTrade, self).__init__(mode)
#         self.name = 'CRYPTO-TRADE'
#         self.full_orderbook = False
#         self.trading_fee = 0.002
#         # need to check on this
#         self.supported_pairs.add_enumerate(['BTC'],['LTC','WDC','FTC','PPC','DVC','DGC','NMC','XPM','TRC','CNC'])
#         self.supported_pairs.add_enumerate(['USD'],['BTC', 'WDC','LTC','XPM','FTC','PPC','NMC'])
#         self.supported_pairs.add_enumerate(['EUR'],['BTC', 'LTC'])
#         self.api = API(key=api_key, secret=secret)
#         # need to retrieve supported pairs
#         self.init_pair_refs()
#
#     def live_order(self, recv_currency, recv_volume, give_currency, give_volume):
#         # cryp.req('trade',{"pair":"ltc_btc","type":"Buy","amount":ltc_bid_amount,"rate":price_to_bid})
#         return NotImplemented
#
#     def update_live_balance(self, currency):
#         account_info= self.api.req('getinfo')
#         account_info['data']['funds']['ltc']
#         return NotImplemented
#
#     def update_orders(self, pair):
#         '''
#         Note: the "pair" coming in may not necessarily be in the order that the
#         exchange supports. We have to specify a
#         '''
#         pairstr, swapped = self.get_pairstr(pair)
#         data = self.api.reqpublic('depth' + '/' + pairstr) # public request
#         if swapped:
#             alt, base = pair
#         else:
#             base, alt = pair
#         for bid in data['bids']:
#             """
#             Documentation is shoddy but it appears to be the price and volume being bought/sold
#             """
#             give_vol = float(bid[1])
#             recv_vol = float(bid[0]) * give_vol
#             order = {"give_currency" : base, \
#                      "recv_currency" : alt, \
#                      "give_volume" : give_vol, \
#                      "recv_volume" : recv_vol }
#             self.orderbook.set_order(order)
#         for ask in data['asks']:
#             recv_vol = float(ask[1])
#             give_vol = float(ask[0]) * recv_vol
#             order = {"give_currency" : alt, \
#                      "recv_currency" : base, \
#                      "give_volume" : give_vol, \
#                      "recv_volume" : recv_vol }
#             self.orderbook.set_order(order)
#
#     def get_pairstr(self, pair):
#         base, alt = pair
#         b = base.lower()
#         a = alt.lower()
#         original = b + "_" + a
#         if original in self.pair_ref:
#             # not flipped
#             return original, False
#
#         flipped = a + "_" + b
#         if flipped in self.pair_ref:
#             return flipped, True
#
#     def init_pair_refs(self):
#         # there IS no index of traded pairs retrievable online
#         # so we have to hardcode it ourselves here
#         self.pair_ref = []
#         self.add_pair_ref(["btc"], ["usd","eur"])
#         self.add_pair_ref(["ltc"], ["usd","eur","btc"])
#         self.add_pair_ref(["nmc","trc","dvc","dgc"],["btc"])
#         self.add_pair_ref(["xpm"],["usd","btc","ppc",])
#         self.add_pair_ref(["ppc","ftc", "wdc"], ["usd","btc"])
#
#     def add_pair_ref(self, bases, alts):
#         for base in bases:
#             for alt in alts:
#                 pid = base + "_" + alt
#                 self.pair_ref.append(pid)