from TriangularArbitrageBot import TriangularArbitrageBot
from broker_utils import create_brokers, print_assets
import config

brokers = create_brokers('BACKTEST', config.PAIRS, config.EXCHANGES)
bot = TriangularArbitrageBot(config, brokers)
print('Initial Position:')
print_assets(bot.brokers)
backtest_data = '/Users/ericjang/Desktop/LiClipse_Workspace/btc_arbitrage/data/Mar-15-2014_14-00-07__30_7200.p'
bot.backtest(backtest_data)
print('Done!')
print('Final Position:')
print_assets(bot.brokers)
