# here is where the pair arbitrage strategy is implemented
# along with the application loop for watching exchanges

from Bot import Bot
from ProfitCalculator import ProfitCalculator

class ArbitrageBot(Bot):
    def __init__(self, config, brokers):
        super(ArbitrageBot, self).__init__(config, brokers)

    def trade_pair(self, pair):
        # - initial test - compare high_bid and low_ask prices
        # - if spread is positive, fetch market depth and re-assess arb opportunity
        base, alt = pair
        pc = ProfitCalculator(self.brokers, pair)
        if pc.check_profits():
            (bidder, asker, profit_obj) = pc.get_best_trade()
            bidder_order = profit_obj["bidder_order"]
            asker_order = profit_obj["asker_order"]
            if self.config.MODE == 'PAPER' or self.config.MODE == 'BACKTEST':

                bidder_tx = 1.0 - bidder.xchg.trading_fee
                asker_tx = 1.0 - asker.xchg.trading_fee
                bidder.balances[base] -= bidder_order.v
                bidder.balances[alt] += bidder_order.p * bidder_order.v * bidder_tx
                asker.balances[base] += asker_order.v * asker_tx
                asker.balances[alt] -= asker_order.p * asker_order.v
                print('Success! Bought %f %s for %f %s from %s and sold %f %s for %f %s at %s' %
                      (asker_order.v*asker_tx,base,asker_order.p* asker_order.v,alt,asker.xchg.name,
                       bidder_order.v,base,bidder_order.p * bidder_order.v * bidder_tx,alt,bidder.xchg.name))
                print('Profit : %f %s' % (bidder_order.p * bidder_order.v * bidder_tx - asker_order.p * asker_order.v, alt))
            else:
                # live trade - do this manually for now!
                print('Profitable Arbitrage Opportunity Detected!! Buy %f %s for %f %s from %s and sell %f %s for %f %s at %s' %
                      (asker_order.v*asker_tx,base,asker_order.p* asker_order.v,alt,asker.xchg.name,
                       bidder_order.v,base,bidder_order.p * bidder_order.v * bidder_tx,alt,bidder.xchg.name))
                print('Profit : %f %s' % (bidder_order.p * bidder_order.v * bidder_tx - asker_order.p * asker_order.v, alt))
#                 asker.buy(pair, asker_order.p, asker_order.v)
#                 bidder.sell(pair, bidder_order.p, bidder_order.v)

