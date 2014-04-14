from ArbitrageBot import ArbitrageBot
from broker_utils import create_brokers
import config_pair as config

brokers = create_brokers('BACKTEST', config.PAIRS, config.EXCHANGES)
bot = ArbitrageBot(config, brokers) # this automatically loads the data path file.
backtest_data = '/Users/ericjang/Desktop/LiClipse_Workspace/btc_arbitrage/data/Mar-29-2014_19-00-35__20_14400.p'
bot.backtest(backtest_data) # start should probably be modified to also allow time ranges (i.e. if i want to run my live trader for 2 hours)
print('done!')
