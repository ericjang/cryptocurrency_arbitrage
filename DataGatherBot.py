# here is where the pair arbitrage strategy is implemented
# along with the application loop for watching exchanges
# For compactness, only the top 10

from Bot import Bot
import cPickle as pickle
import time
from os.path import abspath

class DataGatherBot(Bot):
    def __init__(self, config, brokers):
        super(DataGatherBot, self).__init__(config, brokers)
        self.data_path = abspath(config.TICK_DIR)

    def tick(self):
        #self.log.info('tick')
        super(DataGatherBot, self).tick()

    def start(self, filepath=None, sleep=1, duration=60, maxdepth=6):
        '''
        runs the bot in realtime for 60 seconds, waits 1 second between each execution, and
        write the tick data for playback in realtime. Increase the frequency if you
        are interested in larger-scale price movements rather than high-frequency trading.

        maxdepth is number of orders saved in each market. Idea being that we are unlikely
        to be interested in the order prices of anything beyond the 6th best

        what is the best way to stucture the data?
        ideally we would separate by market, then by bids/asks, then by each broker so it would be easy
        to find prices.
        but actually this would make the broker update mechanism kind of tough from the perspective of the
        actual trading bot. So we will implement it so that the exchange update tick goes as simply as possible
        namely we'll first separate by broker, then by market, then by bids/asks

        this can be quite a lot of data!
        '''
        # generate a filename if one is not provided
        if filepath is None:
            t =  "%s__%s_%s.p" % (time.strftime('%b-%d-%Y_%H-%M-%S'), sleep, duration)
            filepath = self.data_path + '/' + t

        start = time.time()
        data = {'start' : start, 'ticks' : [], 'duration' : duration, 'sleep' : sleep, 'maxdepth' : maxdepth}
        last_tick = start - sleep
        while (time.time() - start < duration and not self.error):
            delta = time.time() - last_tick
            if (delta < sleep):
                # sleep for the remaining seconds
                time.sleep(sleep-delta)

            self.tick() # calls Bot's update functions
            marketdata = {}
            for broker in self.brokers:
                name = broker.xchg.name
                brokerdata = {}
                for market, d in broker.depth.items():
                    brokerdata[market] = {'bids' : d['bids'][:maxdepth-1], 'asks': d['asks'][:maxdepth-1]}
                marketdata[name] = brokerdata
            data['ticks'].append(marketdata)
            last_tick = time.time()
            pickle.dump(data, open(filepath, 'wb')) # write to file
