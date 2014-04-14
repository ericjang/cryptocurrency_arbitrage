from ArbitrageBot import ArbitrageBot
from broker_utils import create_brokers
import config_pair as config

brokers = create_brokers('PAPER', config.PAIRS, config.EXCHANGES)
bot = ArbitrageBot(config, brokers)
bot.start(sleep=10)

