import config
from utils import total_base_volume
from order import Order

class ProfitCalculator(object):
    """
    class for computing a profit matrix from a given set of brokers
    and their orderbooks.
    USE ONE OF THESE PER PAIR
    (rather than tick since my balances and other pair volumes will
    change if I execute a trade)
    """
    def __init__(self, brokers, pair):
        self.brokers = brokers
        self.pair = pair
        """
        first key = bidder exchange
        second key = asker exchange
        spread['CRYPTSY']['COINSE'] = -0.1 # raw profits (bid - ask)
        """
        self.prices = {}        # maintains hi_bids and lo_asks for each broker
        self.balances = {}      # base and alt balances for each exchange
        self.profit_spread = {} # price spreads with transaction fees applied
        self.profits = {}       # actual ALT profits, accounting for balances and volumes

        self.update_balances()
        self.update_profit_spread() # automatically perform calculations upon initialization

    def update_profit_spread(self):
        # computes the profit spread, accounting for trading fees
        self.profit_spread = {b.xchg.name:{a.xchg.name : 0 for a in self.brokers} for b in self.brokers}
        self.prices = {b.xchg.name : {"bid": b.get_highest_bid(self.pair),
                                 "ask": b.get_lowest_ask(self.pair)}  for b in self.brokers}
        for bidder in self.brokers: # bidder names
            for asker in self.brokers: # asker names
                (b,a) = (bidder.xchg.name, asker.xchg.name)
                hi_bid = self.prices[b]['bid']
                lo_ask = self.prices[a]['ask']
                if hi_bid is None or lo_ask is None:
                    self.profit_spread[b][a] = None
                else:
                    # ALT profit with fees applied
                    self.profit_spread[b][a] = self.get_profit_spread(bidder.xchg.trading_fee,hi_bid,asker.xchg.trading_fee,lo_ask)

    def update_balances(self):
        base, alt = self.pair
        for broker in self.brokers:
            self.balances[broker.xchg.name] = { "base" : broker.balances.get(base,0),
                                               "alt" : broker.balances.get(alt,0) }

    def check_profits(self):
        # examine each pair for profits. A number of trivial reject tests are performed:
        # 0) needs to have a positive profit spread to begin with that exceeds 0.01 USD
        # 1) account needs to have sufficient balance to fill the minimum order volume
        # 2) after computing the max tradeable volume (limited by my balance),
        # trade needs to profit at least 0.01 USD.
        base, alt = self.pair
        success = False
        self.profits = {b.xchg.name:{a.xchg.name : None for a in self.brokers} for b in self.brokers}
        for bidder in self.brokers: # bidder names
            for asker in self.brokers: # asker names
                (b,a) = (bidder.xchg.name, asker.xchg.name)
                spread = self.profit_spread[b][a]
                # print(spread)
                if spread is not None and spread > config.PROFIT_THRESH[alt]: # must profit > 0.01 USD to trade at all
                    # Algorithm: iteratively increase the volume on the volume-limited
                    # exchange until profits stop increasing (i.e. arb opportunity lost)
                    # ideally we want to increase BOTH until profits no longer increase,
                    # but that introduces an icky optimization problem
                    # temporary solution: trade EXACTLY the min volume base order
                    # thereby saving you the trouble of deciding which to fix, etc.
                    # (note: we will scale appropriately to account for trading fees)
                    slug = base + "_" + alt
                    bids = bidder.depth[slug]['bids']
                    asks = asker.depth[slug]['asks']
                    profit_obj = self.calculate_order(bidder, bids, asker, asks)
                    # after calculating the order, even though the spread is profitable, our balances make it not possible.
                    # i.e. small magnitudes, requires too much shuffling money around to profit such a small amount.
                    if profit_obj is not None and profit_obj["profit"] > config.PROFIT_THRESH[alt]:
                        self.profits[b][a] = profit_obj
                        success = True

        return success # return True if there are any profits at all


    def calculate_order_simple(self, bidder, bids, asker, asks):
        """
        in my original algorithm design, we traverse the depth to fill the minimum
        volume desired. this is too complicated and hairy.
        instead, i will only proceed if the top order volume naturally exceeds
        the best price. cases where the second best is ``hidden'' under a small order
        will be ignored for now.
        """
        base, alt = self.pair
        """
        first check - do the best orders have sufficient volume to satisfy xchg minimums?
        """
        bidder_min_base_vol = bidder.xchg.get_min_vol((base,alt), None) # temp hack - in pair arbitrage we assume we're always trading on valid markets
        asker_min_base_vol = asker.xchg.get_min_vol((base,alt), None)
        min_base_vol = min(bidder_min_base_vol, asker_min_base_vol) # remember, we have to trade approx same amount
        if (bids[0].v < min_base_vol):
            print('%s insufficient best order volume to satisfy min trade: %f' % (bidder.xchg.name, bids[0].v))
            return None
        if (asks[0].v < min_base_vol):
            print('%s insufficient best order volume to satisfy min trade: %f' % (asker.xchg.name, asks[0].v))
            return None


        """
        next thing to check - see if we have enough funds to make the trade
        """
        bidder_base_balance = self.balances[bidder.xchg.name]['base'] # check how much base we can afford to sell to bidder
        asker_alt_balance = self.balances[asker.xchg.name]['alt']
        asker_base_afford = asker_alt_balance / self.prices[asker.xchg.name]['ask'] # check how much base we can afford to buy from asker
        poor = False
        if (bidder_base_balance < min_base_vol):
            print(bidder.xchg.name)
            print('Can\'t afford min vol trade - insufficient bidder balance!')
            print('\t %s +%f %s' % (bidder.xchg.name, bidder_min_base_vol - bidder_base_balance, base))
            poor = True

        if (asker_base_afford < min_base_vol):
            print('Can\'t afford min vol trade - insufficient asker balance!')
            print('\t %s +%f %s' % (asker.xchg.name, (asker_min_base_vol-asker_base_afford)*self.prices[asker.xchg.name]['ask'], alt))
            poor = True

        if poor:
            return None

        """
        size the volume of base traded
        """
        asker_tx = 1.0 - asker.xchg.trading_fee
        bidder_tx = 1.0 - bidder.xchg.trading_fee

        # TODO - weird shit going on here, fix this!!

        # the line below computes how much base we could trade if we had unlimited balance
        # but are limited by the order volumes of base between the exchanges.
        # we receive a maximum of asks[0].v * asker_tx units of base from the asker
        # and we can sell a maximum of bids[0].v to the bidder
        max_base_xchg = min(bids[0].v, asks[0].v * asker_tx)
        # computes how much base we could trade if we had unlimited volume, limited balance
        max_base_balance = min(bidder_base_balance, asker_base_afford)
        # how much we will end up buying and selling
        base_vol = min(max_base_xchg, max_base_balance)

        bidder_order = Order(bids[0].p, base_vol)
        asker_order = Order(asks[0].p, base_vol / asker_tx)
        # profit in units alt (BTC)
        net_base = asker_order.v * asker_tx - bidder_order.v
        net_alt = bidder_order.p * bidder_order.v * bidder_tx - asker_order.p * asker_order.v
        # this is the final checkpoint - if the trade's profits are too small compared to the amount of BTC
        # we have to move, then the trade is probably too risky to make.
        if net_alt/(asker_order.p * asker_order.v) < config.BTC_RISK:
            print('Order volume too large to justify risk of performing the trade')
            return None
        else:
            return {
                "bidder_order":bidder_order,
                "asker_order":asker_order,
                "profit":net_alt
                }


    def calculate_order(self, bidder, bids, asker, asks):
        '''
        given a bidder and asker broker and a list of bids/asks to compute,
        - returns the order that you submit to the bidder (sell), the order that you
        submit to the asker (buy) and the profit in alt
        note, profit might be negative, if the spread across the order volumes
        are not good enough
        '''
        return self.calculate_order_simple(bidder, bids, asker, asks)
#         base, alt = self.pair
#
#         bidder_min_base_vol = bidder.xchg.get_min_vol((base, alt),None)
#         asker_min_base_vol = asker.xchg.get_min_vol((base, alt),None)
#         min_base_vol = min(bidder_min_base_vol, asker_min_base_vol)
#
#         bidfee = bidder.xchg.trading_fee
#         askfee = asker.xchg.trading_fee
#         bids = self.clip_orders(bids, min_base_vol)
#         # small subtlety - we receive slightly
#         # less than the min volume so to cover our arbitrage
#         # properly we scale up the ask volume slightly
#         padded_buy_vol = min_base_vol * 1.0/(1.0 - askfee)
#         asks = self.clip_orders(asks, padded_buy_vol)
#
#         # check profits
#         bid_alt_recv = (1.0-bidfee) * sum([b.p*b.v for b in bids]) # units of alt to recv
#         ask_alt_give = sum([a.v*a.p for a in asks]) # units of alt to give
#         profit = bid_alt_recv - ask_alt_give
#         if profit > config.PROFIT_THRESH[alt]:
#             print('WOOHOO! Profitable, EXECUTABLE arbitrage detected')
#             bidder_order = (bids[-1].p , min_base_vol) # sell at the "lowest" price of profitable asks to fill as much as possible
#             asker_order  = (asks[-1].p , padded_buy_vol)  # buy at the "highest" price of profitable bids to fill as much as possible
#         else:
#             bidder_order, asker_order, profit = (None, None, profit)
#         return {
#                 "bidder_order":bidder_order,
#                 "asker_order":asker_order,
#                 "profit":profit,
#                 "bidder_recv":bid_alt_recv,
#                 "bidder_give":min_base_vol,
#                 "asker_give":ask_alt_give,
#                 "asker_recv":min_base_vol
#                 }

    def clip_orders(self, orders, desired_volume):
        # given an array of bid or ask orders,
        # and a desired volume, resize the orders so that
        # the total volume == desired_volume
        #total_volume = lambda arr : sum([a.v for a in arr])
        # volume = total_volume(orders) # original volume, in units base
        i = 1
        while total_base_volume(orders[:i]) < desired_volume:
            i += 1
            if i > len(orders):
                # not enough orders in the orderbook!
                break
        # more than likely, adding on the last order tacked on a bit of overshoot.
        # the remainder MUST be spanned by last order (i.e. cannot be in the second
        # to last otherwise we would have caught it)
        if desired_volume is None:
            wtf = 1

        remainder = total_base_volume(orders[:i]) - desired_volume
        last_order = orders[i-1]
        orders[i-1] = Order(last_order.p, last_order.v - remainder)
        return orders[:i]

    def get_best_trade(self):
        # returns the bidder exchange, asker exchange,
        # buy order (price, volume) and ask order (price, volume)
        # TODO
        best_profit = 0.0
        best_profit_obj = None
        hi_bidder = None
        lo_asker = None
        for bidder in self.brokers:
            for asker in self.brokers:
                (b,a) = (bidder.xchg.name, asker.xchg.name)
                profit_obj = self.profits[b][a]
                if profit_obj is not None:
                    if profit_obj["profit"] > best_profit:
                        best_profit = profit_obj["profit"]
                        best_profit_obj = profit_obj
                        hi_bidder = bidder
                        lo_asker = asker

        return (hi_bidder, lo_asker, best_profit_obj)


    def get_profit_spread(self, bidder_fee, bid_price, asker_fee, ask_price):
        # simple formula
        # explanation: if hi_bid = 110 and lo_ask = 100
        # then lo_ask will only return 0.998 units per 1 paid
        # I am selling base to the bidder at a rate of 110 per unit given
        # but i actually want to only sell 0.998 units (to match ask recv volume) < -- wait what???
        # so I scale by 0.998
        # finally, the bid order itself has an exchange fee so I only see 0.998 of *that*
        # NOTE: this does not take actual order volumes into account, so this is not
        # representative of what actual profits would be
        return bid_price*(1 - asker_fee) * (1.0 - bidder_fee) - ask_price

#     def print_matrix(self, matrix):
#         """
#         pretty-prints a matrix
#         useful in displaying things like gross profit spreads and such
#         """
#         s = [[str(e) for e in row] for row in matrix]
#         lens = [max(map(len, col)) for col in zip(*s)]
#         fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
#         table = [fmt.format(*row) for row in s]
#         print '\n'.join(table)
