import config
from order import Order
import utils

class TriangleProfitCalculator(object):
    """
    Profit calculator for single-exchange triangular arbitrage, trading
    minimum arbitrage volumes.
    all this data will be computed for a SINGLE exchange SINGLE pair
    (by single pair, I am referring to the start/end currencies of the arbitrage).
    therefore, data structures are different from ProfitCalculator
    """
    def __init__(self, broker, pair, roundtrip_currencies):
        self.broker = broker
        self.pair = pair
        self.roundtrip_currencies = roundtrip_currencies
        """
        self.type1_spreads take the form of {'C1' : 0.1245, 'C2' : 0.54321}
        """
        self.type1_spreads = {}
        self.type2_spreads = {}
        """
        self.type2_spreads take the form of
        {
            'C1' : {
                'orders' : [<Order>,<Order>,<Order>]
                'profit' : 12.345
            },
            'C2' : {
                'orders' :
                'profit' :
            }
        }
        """
        self.type1_roundtrips = {}
        self.type2_roundtrips = {}

    def check_profits(self, type):
        """
        returns True if profitable round-trip exists between any 3 currencies.
        checks for spread between implied_hi_bid and market lo_ask
        """
        if type == 1: # implied_hi_bid - lo_ask > 0
            return self.check_type1_profits()
        elif type == 2: # hi_bid - implied_lo_ask > 0
            return self.check_type2_profits()

    def check_type1_profits(self):
        """
        yes, there is a lot of rendundancy code between check_type1_profits
        and check_type2_profits, but this code is much more readable
        """
        base, alt = self.pair
        tx = 1 - self.broker.xchg.trading_fee
        lo_ask = self.broker.get_lowest_ask(self.pair)
        count = 0
        for C in self.roundtrip_currencies:
            # calculate implied hi bid rate
            sell_A_C = self.broker.get_highest_bid((base,C))
            sell_C_B = self.broker.get_highest_bid((C,alt))
            if sell_A_C is None:
                print('Empty %s_%s bid orders, skipping...' % (base,C))
                continue
            if sell_C_B is None:
                print('Empty %s_%s bid orders, skipping...' % (C,alt))
                continue
            # this is how much base we would get if we sold exactly 1 unit of alt
            implied_hi_bid = (sell_A_C * tx) * (sell_C_B * tx)
            # see type2 calculation for explanation
            spread = implied_hi_bid * tx - lo_ask
            self.type1_spreads[C] = spread
            if spread > config.PROFIT_THRESH[alt]:
                count += 1
        #if count > 0:
        #    print('detected %d profitable spreads!' % count)
        return (count > 0)

    def check_type2_profits(self):
        base, alt = self.pair
        tx = 1 - self.broker.xchg.trading_fee
        hi_bid = self.broker.get_highest_bid(self.pair)
        count = 0
        for C in self.roundtrip_currencies:
            # calculate implied lo ask rate
            buy_C_B = self.broker.get_lowest_ask((C,alt))
            buy_A_C = self.broker.get_lowest_ask((base,C))
            # how many alts it would REALLY cost me to buy 1 unit of base (i.e. end up with exactly 1 unit of base)
            implied_lo_ask = (buy_C_B * 1.0/tx) * (buy_A_C * 1.0/tx)
            # hi_bid is multiplied by tx one more time because thats how much alts we recv for selling 1 unit of base
            # and subtract from that the amount of alts we pay exactly for 1 unit of base
            spread = hi_bid * tx - implied_lo_ask
            self.type2_spreads[C] = spread
            if spread > config.PROFIT_THRESH[alt]:
                count += 1
        #if count > 0:
        #    print('detected %d profitable spreads!' % count)
        return (count > 0)

    def get_best_roundtrip(self, type):
        """
        calculate the optimal roundtrip for you to execute
        takes the form of 3 trades that are computed to fill specific quantities of orders
        in each of 3 different markets in a single exchange.
        """
        # the code is very much similar.
        if type == 1:
            return self.get_best_type1_roundtrip()
        elif type == 2:
            return self.get_best_type2_roundtrip()


    def get_best_type1_roundtrip(self):
        """
        sell(AC), sell(CB)
        buy(AB)
        """
        A,B = self.pair # use A_B notation instead of base, alt
        b = self.broker
        alt = B
        tx = 1 - b.xchg.trading_fee
        asks_ab = b.get_orders((A,B), 'asks') # people who are selling A_B
        for C, spread in self.type1_spreads.items():
            if spread > config.PROFIT_THRESH[alt]:
                self.type1_roundtrips[C] = {}
                bids_ac = b.get_orders((A,C), 'bids') # people who are buying A_C
                bids_cb = b.get_orders((C,B), 'bids') # people who are buying C_B
                # minimum volume constraints
                min_ac = b.xchg.get_min_vol((A,C), bids_ac) # how much DOGE we have to sell in the first trade
                min_cb = b.xchg.get_min_vol((C,B), bids_cb) # how much LTC we have to sell in the second trade
                min_ab = b.xchg.get_min_vol((A,B), asks_ab) # how much DOGE we have to buy in the third trade
                # assuming value A << value C, first trade has to acquire enough LTC to perform the second trade
                bids_ac_clipped = b.xchg.get_clipped_alt_volume(bids_ac, min_ac/tx)
                # how much DOGE we sold to acquire 0.01 LTC
                v1 = utils.total_base_volume(bids_ac)
                # performing the second trade will net enough BTC to buy back at least 0.01 DOGE
                bids_cb_clipped = b.xchg.get_clipped_base_volume(bids_cb, min_ac)
                # buy back exactly how much DOGE we spent in the first place
                asks_ab_clipped = b.xchg.get_clipped_base_volume(asks_ab, v1/tx)
                # construct the orders
                o1 = Order(utils.lowest_price(bids_ac_clipped), utils.total_base_volume(bids_ac_clipped), type="sell", pair=(A,C))
                o2 = Order(utils.lowest_price(bids_cb_clipped), utils.total_base_volume(bids_cb_clipped), type="sell", pair=(C,B))
                o3 = Order(utils.highest_price(asks_ab_clipped), utils.total_base_volume(asks_ab_clipped), type="buy", pair=(A,B))
                # test orders for profitability
                self.type1_roundtrips[C]["orders"] = [o1, o2, o3]

                netA = -o1.v + o3.v * tx
                netB = utils.total_alt_volume(bids_cb_clipped) * tx - utils.total_alt_volume(asks_ab_clipped)
                netC = utils.total_alt_volume(bids_ac_clipped) * tx - o2.v

                self.type1_roundtrips[C]["profit"] = netB
                print('check...')
        return self._get_highest_profit(self.type1_roundtrips)

    def get_best_type2_roundtrip(self):
        """
        [Buy(C_B)Buy(A_C)] Sell(A_B)
        """
        A,B = self.pair # use A_B notation instead of base, alt
        b = self.broker
        alt = B
        tx = 1 - b.xchg.trading_fee
        bids_ab = b.get_orders((A,B), 'bids') # people who are selling A_B
        for C, spread in self.type2_spreads.items():
            if spread > config.PROFIT_THRESH[B]:
                self.type2_roundtrips[C] = {}
                asks_cb = b.get_orders((C,B), 'asks') # people who are buying C_B
                asks_ac = b.get_orders((A,C), 'asks') # people who are buying A_C

                # minimum volume constraints
                min_cb = b.xchg.get_min_vol((A,C), asks_cb) # how much DOGE we have to sell in the first trade
                min_ac = b.xchg.get_min_vol((C,B), asks_ac) # how much LTC we have to sell in the second trade
                min_ab = b.xchg.get_min_vol((A,B), bids_ab) # how much DOGE we have to buy in the third trade

                asks_cb_clipped = b.xchg.get_clipped_base_volume(asks_cb, min_cb) # buy exactly minimum quantity
                asks_ac_clipped = b.xchg.get_clipped_alt_volume(asks_ac, min_cb*tx) # can probably spend less than 0.01 LTC buying 0.01 DOGE
                v3 = utils.total_base_volume(asks_ac_clipped) * tx # total DOGE we receive
                bids_ab_clipped = b.xchg.get_clipped_base_volume(bids_ab, v3) # sell all the DOGE for BTC

                # construct the orders that we submit
                o1 = Order(utils.highest_price(asks_cb_clipped), utils.total_base_volume(asks_cb_clipped), type="buy", pair=(C,B))
                o2 = Order(utils.highest_price(asks_ac_clipped), utils.total_base_volume(asks_ac_clipped), type="buy", pair=(A,C))
                o3 = Order(utils.lowest_price(bids_ab_clipped), utils.total_base_volume(bids_ab_clipped), type="sell", pair=(A,B))

                self.type2_roundtrips[C]["orders"] = [o1, o2, o3]
                # these calculations should adequately take volume into account
                netA = o2.v * tx - o3.v
                netB = - utils.total_alt_volume(asks_cb_clipped) + utils.total_alt_volume(bids_ab_clipped) * tx
                netC = o1.v * tx - utils.total_alt_volume(asks_ac_clipped)

                self.type2_roundtrips[C]["profit"] = netB
                print('check ... ')
        # loop through C and choose the one with the largest profit
        return self._get_highest_profit(self.type2_roundtrips)

    def _get_highest_profit(self, roundtrips):
        max_profit = 0.0
        best_C = None
        for C, result in roundtrips.items():
            if "profit" in result and result["profit"] > max_profit:
                max_profit = result["profit"]# all profits should be in units ALT anyway
                best_C = C
        if best_C is not None:
            return roundtrips[best_C]["orders"]
        else:
            return None


