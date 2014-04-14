# NOTE: all rates and currencies multiplied by 10^8 to avoid floating point!
# this will be a very important consideration

from Exchange import Exchange
from coinex_api import CoinExAPI
from myutils import get_swapped_order
from order import Order

class CoinEx(Exchange):
    def __init__(self, api_key, secret):
        self.api = CoinExAPI(api_key, secret)
        super(CoinEx, self).__init__()
        self.name = 'COINEX'
        self.trading_fee = 0.002
        self.marketids = {}

    def get_tradeable_pairs(self):
        tradeable_pairs = []
        self.pairIDs = {}       # also initialize pairID reference while we're at it
        trade_pairs = self.api.get_trade_pairs()
        for pair in trade_pairs["trade_pairs"]:
            pairID = str(pair["id"])
            currencies = pair["url_slug"].split("_")
            base = currencies[0].upper()
            alt = currencies[1].upper()
            tradeable_pairs.append((base, alt))
            slug = base + "_" + alt
            self.pairIDs[slug] = pairID
        return tradeable_pairs

    def get_depth(self, base, alt):
        """
        coinEx does not support retrieving all depths! GRRRR
        TODO - need to also append orderID!!!
        """
        pair0 = (base, alt)
        pair, swapped = self.get_validated_pair(pair0)
        newbase, newalt = pair
        pairID = self.get_pairID(newbase, newalt)
        orders = self.api.get_orders(pairID)
        book = { "bids" : [], "asks" : [] }
        for data in orders["orders"]:
            if not data["complete"]:
                price = float(data["rate"]*1e-8)
                volume = float(data["amount"]*1e-8)
                order = Order(price, volume, orderID=data['id'], timestamp=data['created_at'])
                if not swapped:
                    if data['bid']: # buy order
                        book['bids'].append(order)
                    else: # sell order
                        book['asks'].append(order)
                else: # is swapped
                    order = get_swapped_order(order)
                    if data['bid']:
                        book['asks'].append(order)
                    else:
                        book['bids'].append(order)

        return book


    def get_balance(self, currency):
        '''
        warning: dont call this too often.
        use get_all_balances instead
        '''
        balances = self.api.get_balances()
        for c in balances["balances"]:
            if currency == c["currency_name"]:
                return c["amount"] * 1e-8
        return 0.0

    def get_all_balances(self):
        data = self.api.get_balances()
        balances = {c["currency_name"] : c["amount"]*1e-8 for c in data['balances']}
        return balances

    def submit_order(self, gc, gv, rc, rv):
        return NotImplemented
    #    pair0 = (gc, rc)
   #     pair, swapped = self.get_validated_pair(pair0)
  #      newbase, newalt = pair
 #       pairID = self.get_pairID(newbase, newalt)

        # TODO, do maths here

#        self.api.submit_order(self, pairID, amount, order_type, rate)

    def confirm_order(self, orderID):
        data = self.api.get_order_status(orderID)
        # TODO

    # borrowed from Cryptsy API
    def get_pairID(self, base, alt):
        if (base, alt) in self.tradeable_pairs:
            slug = base + "_" + alt
            return self.pairIDs[slug]
        elif (alt, base) in self.tradeable_pairs:
            slug = alt + "_" + base
            return self.pairIDs[slug]
        else:
            return 'ERROR!'
