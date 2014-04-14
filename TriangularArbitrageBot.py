# Triangular Arbitrage Bot
# SINGLE exchange algorithm -> allows for near-instantaneous arbitrage without
# necessitating positions in multiple currencies.

from Bot import Bot, UpdateBalanceThread, UpdateDepthThread
from TriangleProfitCalculator import TriangleProfitCalculator
import time

class TriangularArbitrageBot(Bot):
    def __init__(self, config, brokers):
        super(TriangularArbitrageBot, self).__init__(config, brokers)
        # this bot only trades on ONE broker!!!
        # the reason I am doing this is to make the initial prototype system more robust to failure
        # i.e. others keep trading even if one exchange fails.
        if len(self.brokers) > 1:
            self.log.warning("TriangleArbitrageBot only trades on one exchange! Ignoring the others...")
        self.broker = self.brokers[0]
        self.init_cross_markets()

    def get_roundtrip_currencies(self, pair):
        """
        given market A_B, returns an array of all tradeable currencies C if
        the exchange supports markets (A_C or C_A) and (B_C or C_B).
        """
        base, alt = pair
        xchg = self.broker.xchg
        currencies = []
        for C in xchg.tradeable_currencies:
            if (xchg.get_validated_pair((base, C)) is not None) and (xchg.get_validated_pair((alt, C)) is not None):
                currencies.append(C)
        return currencies

    def init_cross_markets(self):
        """
        stores which orderbook depths to also update when
        calculating spreads for a single pair
        cross-markets data structure:
        {
        'Vircurex' : {
                'A_B' : ['C',etc.] # A_B is the pair that we wish to trade
                'D_E' : ['F','G', etc.]
            },
        etc.
        }
        """
        self.cross_market_currencies = {}
        self.update_pairs = {}
        for pair in self.config.PAIRS:
            if self.broker.xchg.get_validated_pair(pair) is not None:
                base, alt = pair
                slug = base + '_' + alt
                self.cross_market_currencies[slug] = self.get_roundtrip_currencies(pair)
                # for broker update, we will also need to pass in the actual pairs to update
                # so might as well pre-compute the explicit pairs as well.
                self.update_pairs[slug] = [pair] # after all, this is the most important one to update!
                for cm in self.cross_market_currencies[slug]:
                    if cm not in ['USD', 'CNY', 'EUR']: # ignore fiat currency for the time being
                        self.update_pairs[slug].append((base, cm))
                        self.update_pairs[slug].append((cm, alt))
            print('update pairs for %s: %s' % (slug, self.update_pairs[slug]))

    def tick(self):
        """
        instead of looping over each pair, it makes more sense to trade one broker at a time
        (otherwise if we update all the brokers first and then trade each pair, slippage time increases!)
        """
        self.log.info('tick')
        self.broker.clear()
        # we could update the ENTIRE depth here but
        # it turns out that some exchanges trade FAR more currencies than we want to see.
        # better to just update on each pair we trade (after all, we affect the orderbook)
        for pair in self.config.PAIRS:
            slug = pair[0] + '_' + pair[1]
            if self.backtest_data is not None:
                self.broker.update_multiple_depths(self.update_pairs[slug], self.backtest_data, self.tick_i)
            else:
                self.broker.update_multiple_depths(self.update_pairs[slug])
            # if we are in gathering mode, do not trade!
            if self.trading_enabled:
                self.trade_pair(self.broker, pair)

    def trade_pair(self, broker, pair):
        """
        unlike the cross-exchange arbitrage bot, this one only trades
        one exchange at a time!
        """
        base, alt = pair
        slug = base + '_' + alt
        pc = TriangleProfitCalculator(broker, pair, self.cross_market_currencies[slug])
        # type1 and type2 roundtrips are in fact completely mutually exclusive!
        # that means that if we detect both type1 and type2 roundtrips, we can simultaneously
        # execute both without worrying about moving the market.
        for type in [1,2]:
            if pc.check_profits(type):
                print('Potentially Profitable Type%d Spread' % type)
                order_triplet = pc.get_best_roundtrip(type)
                if order_triplet is not None:
                    print('Submitting Arbitrage Trades...')
                    # submit each order in sequence.

                #if order_triplet is not None:
                #    print('Type%d Arbitrage Opportunity Detected!' % type)
                    # submit each order



#                 triplet = pc.get_best_roundtrip()
#                 for (bidder, order) in triplet:
                # for now, just print the order, test to see if you can execute manually.
                # order_id, t = bidder.submit(order)

#                     # production TODO - each broker automatically cancels orders if they don't go through.
#                     while not bidder.confirm_order(order_id):
#                         # if time.time() - t > 3:
#                         error = bidder.order_error(order_id)
#                 else:
#                     print('round trip incurred an error')

                    # wait
                    # if time > threshold, swallow losses
                    # and cancel this one
                    # and don't submit all remaining orders

