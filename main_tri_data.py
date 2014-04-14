from DataGatherBot import DataGatherBot
from TriangularArbitrageBot import TriangularArbitrageBot
from broker_utils import create_brokers
import config_tri as config

brokers = create_brokers('PAPER', config.PAIRS, config.EXCHANGES)
tribot = TriangularArbitrageBot(config, brokers)
tribot.gather_data(sleep=30, duration= 60 * 60 * 4, maxdepth=4) # 4 hours of data!

print('Done!')