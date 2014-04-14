# class for Broker
import sys
from myutils import get_swapped_order

class Broker(object):
    def __init__(self, mode, xchg):
        super(Broker, self).__init__()
        self.mode = mode # TRADING mode (PAPER or LIVE)
        self.xchg = xchg

        # stores live balances
        self.balances = {}

        #  self. depth consists of keys = the bases that I define in config, and each lists buy/sell orders
        #  for that market. However, the exchange subclass implementation should take care of whether I
        #  flip my market slugs or not.
        self.depth = {}
        self.orders = [] # list of outstanding orders

    def get_highest_bid(self, pair):
        base, alt = pair
        slug = base + "_" + alt
        if slug in self.depth and len(self.depth[slug]['bids']) > 0:
            return self.depth[slug]['bids'][0].p
        swapped_slug = alt + "_" + base
        if swapped_slug in self.depth and len(self.depth[swapped_slug]['asks']) > 0:
            print('WEIRD, this shouldn\'t being getting called!')
            ask = self.rates[swapped_slug]['asks'][0]
            return get_swapped_order(ask).p
        return None

    def get_lowest_ask(self, pair):
        base, alt = pair
        slug = base + "_" + alt
        if slug in self.depth and len(self.depth[slug]['asks']) > 0:
            return self.depth[slug]['asks'][0].p
        swapped_slug = alt + "_" + base
        # note - there should actually be no reason that the swapped low ask gets called, because we are already fetching
        # all the depths in the order that we would actually see them!
        if swapped_slug in self.depth and len(self.depth[swapped_slug]['bids']) > 0:
            print('WEIRD, this shouldn\'t being getting called!')
            bid = self.rates[swapped_slug]['bids'][0]
            return get_swapped_order(bid).p
        return None

    def get_orders(self, pair, type):
        """
        use this function for accessing the depth info

        Note that the depth retrieval already flips the order for us based on the ordering
        that we specified during pair updates. However those pair update orders are arbitrary
        and we may end up needing both buy(A_B) and sell(B_A) orders with the samedepth info.
        (TODO - confirm whether the swapped retrieval ever gets called!)
        we could pre-compute the depth information but it would double the
        serialized data size. so it's probably easier for now just to re-compute on the
        fly when we need it again.

        type = 'bids' or 'asks'
        """
        base, alt = pair
        slug = base + '_' + alt
        if slug in self.depth:
            return self.depth[slug][type]
        # damn, it's flipped. do we ever actually cross this point?
        swapped_slug = alt + '_' + base
        if swapped_slug in self.depth:
            opposite = 'bids' if type is 'asks' else 'asks'
            return [get_swapped_order(o) for o in self.depth[swapped_slug][opposite]]

    def update_depth(self, pair, backtest_data=None, tick_i=0):
        # updates the highest_bid and lowest_ask for given pair
        # depths are sorted by best first
        base, alt = pair
        slug = base + "_" + alt
        if backtest_data is not None:
            # load in backtest data provided by the bot
            try:
                self.depth[slug] = backtest_data['ticks'][tick_i][self.xchg.name][slug]
            except:
                print('uh oh, missing depth data from this exchange')
                self.depth[slug] = {"bids":[],"asks":[]}
            """
            TODO - if backtesting, need to modify depth so that it appears as if we had
            actually moved the market with our previous orders.

            i.e. if an orderID we have acted on shows up in the depth list, modify it.
            """
        else:
            try:
                self.depth[slug] = self.xchg.get_depth(base, alt)
                # sort the depth by descending bid price and ascending ask price
                self.depth[slug]['bids'].sort(key=lambda x: x.p, reverse=True)
                self.depth[slug]['asks'].sort(key=lambda x: x.p, reverse=False)
            except:
                self.depth[slug] = {'bids':[],'asks':[]} # keep going
                e = sys.exc_info()[0]
                print('%s error: %s' % (self.xchg.name, e))


    def update_multiple_depths(self, pairs, backtest_data=None, tick_i=0):
        if backtest_data is not None:
            # load in backtest data provided by bot
            self.depth = backtest_data['ticks'][tick_i][self.xchg.name]
            """
            TODO - it is very likely that when backtesting, we will see an opportunity come up
            multiple times on several ticks, even across large intervals like 1 minute
            (liquidity of bitcoin is low, and I suspect not many are doing HFT arbitrage with bitcoin)

            to handle this, we have to simulate partial/complete filling of orders based on orderID
            for example, if a bid order was selling 0.4 BTC and I bought 0.2 BTC from that order,
            the next tick will probably still display 0.4BTC being sold. I need to deduct 0.2 on the next tick
            """

        else:
            # try
            # assume that we have called broker.clear() before this.
            # remove all pairs that have already been updated in brokers!

            for (A,B) in pairs:
                slug = A + '_' + B
                if slug in self.depth:
                    pairs.remove((A,B)) # already has been updated!

            self.depth.update(self.xchg.get_multiple_depths(pairs))
            # sort the depths by descending bid price and ascending ask price
            # some depths have already been updated
            for (A,B) in pairs:
                slug = A + '_' + B
                self.depth[slug]['bids'].sort(key=lambda x: x.p, reverse=True)
                self.depth[slug]['asks'].sort(key=lambda x: x.p, reverse=False)
#             except:
#                 e = sys.exc_info()[0]
#                 print(e)

    def update_all_balances(self):
        # key method!! when running in paper/live mode, fetch data from xchg
        # when running in backtest mode, this is a SIMULATED quantity!
        if (self.mode == 'LIVE'):
            self.balances = self.xchg.get_all_balances()
        elif (self.mode == 'PAPER' or self.mode == 'BACKTEST'):
            pass

    def clear(self):
        # only clear balance if we are not backtesting.
        if self.mode == 'PAPER' or self.mode == 'LIVE':
            self.balances = {}
        self.depth = {}

    def buy(self, pair, price, volume):
        pass

    def sell(self, pair, price, volume):
        pass

    def submit_order(self, pair, ordertype, price, volume):
        # submit order via API
        pass