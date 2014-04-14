from Exchange import Exchange
from pyvircurex.common import public_request, secure_request, make_token
from pyvircurex.account import Account
from pyvircurex.data import Pair
from order import Order


# this implementation assumes you are using the same security word for all
# API calls!

class Vircurex(Exchange):
    def __init__(self, user, security_word):
        super(Vircurex, self).__init__()
        self.account = Account(user, security_word)
        self.name = 'VIRCUREX'
        self.trading_fee = 0.002

    def get_tradeable_pairs(self):
        # 23 Mar 2014- need to update this to reflect recent changes
        # don't trade between anything that does not involve BTC.
        pairs = []
        b = 'BTC'
        alts = ['WDC','DOGE','LTC','PPC','DVC','DGC','ANC','NMC','I0C','USD',
                'XPM','FRC','TRC','IXC','EUR','FTC','QRK','NVC','BQC','YAC',
                'CNC','SC','LQC','EUR','USD']
        for a in alts:
            pairs.append((a,b))
        return pairs

    def get_depth(self, base, alt):
        pair = Pair(base + "_" + alt)
        data = pair.orderbook
        #order = Order(price, volume, orderID=data['id'], timestamp=data['created_at'])
        # unfortunately, vircurex doesn't store timestamps or orderIDs
        bids = [Order(float(t[0]), float(t[1])) for t in data['bids']]
        asks = [Order(float(t[0]), float(t[1])) for t in data['asks']]
        return {'bids': bids, 'asks': asks}

    def get_balance(self, currency):
        return self.account.balance(currency)['availablebalance']

    def get_all_balances(self):
        data = self.account.balances()
        balances = {k:float(v['availablebalance']) for k,v in data.items()}
        return balances

    def submit_order(self, gc, gv, rc, rv):
        price = gv/rv
        return self.account.buy(rc, rv, gc, price)

    def release_order(self, orderID):
        return self.account.release_order(orderID)

    def confirm_order(self, orderID):
        pass
