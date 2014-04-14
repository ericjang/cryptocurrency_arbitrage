# performs tick data retrieval to be replayed later.

from DataGatherBot import DataGatherBot
from broker_utils import create_brokers
import config_pair as config

brokers = create_brokers('PAPER', config.PAIRS, config.EXCHANGES)
bot = DataGatherBot(config, brokers)
bot.start(sleep=20, duration=60 * 60 * 4, maxdepth=6) # 5 hours of data, one minute intervals
print('Done!')