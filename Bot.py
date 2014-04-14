# generic class for trading/market-watching bots

# here is where the pair arbitrage strategy is implemented
# along with the application loop for watching exchanges

import threading
import time
from Logger import Logger
from ProfitCalculator import ProfitCalculator
import cPickle as pickle
from os.path import abspath
from order import Order # Order class needs to be present for de-serialization of orders
from broker_utils import get_assets, print_assets

class UpdateDepthThread(threading.Thread):
    """
    simple class for updating the highest bid and lowest
    ask rates of each broker
    """
    def __init__(self, broker, pair, backtest_data=None, tick_i=0):
        self.broker = broker
        self.pair = pair
        self.backtest_data = backtest_data
        self.tick_i = tick_i
        threading.Thread.__init__(self)

    def run(self):
        if self.broker.xchg.get_validated_pair(self.pair) is not None:
            if self.backtest_data is not None:
                self.broker.update_depth(self.pair, self.backtest_data, self.tick_i)
            else:
                self.broker.update_depth(self.pair)

class UpdateBalanceThread(threading.Thread):
    """
    simple thread class for updating balances across
    all accounts. Originally this was a part of UpdateDepthThread
    but some exchanges serve up entire wallet and this may result in
    HTTP 429 error if too many requests are made!
    """
    def __init__(self, broker):
        self.broker = broker
        threading.Thread.__init__(self)
    def run(self):
        self.broker.update_all_balances()

class Bot(object):
    def __init__(self, config, brokers):
        """
        config = configuration file
        brokers = array of broker objects
        """
        super(Bot, self).__init__()
        self.config = config
        self.brokers = brokers
        self.error = False
        self.log = Logger()
        self.backtest_data = None
        self.max_ticks = 0
        self.data_path = abspath(config.TICK_DIR)
        self.trading_enabled = True
        self.tick_i = 0

    def start(self, sleep=0): # for live/paper trading
        start = time.time()
        last_tick = start - sleep
        while not self.error:
            delta = time.time() - last_tick
            if (delta < sleep):
                # sleep for the remaining seconds
                time.sleep(sleep-delta)
            self.tick()
            last_tick = time.time()

    def backtest(self, backtest_file): # for backtesting
        print('Initial Position:')
        initial_position = get_assets(self.brokers)
        print(initial_position)
        self.backtest_data = pickle.load(open(backtest_file, "rb" ))
        self.max_ticks = len(self.backtest_data['ticks'])
        self.tick_i = 0
        while self.tick_i < self.max_ticks:
            self.tick()
            self.tick_i += 1
        # print final assets
        print('Final Position:')
        final_position = get_assets(self.brokers)
        # compute total profits
        print('Total Profits:')
        for k,v in final_position.items():
            if k in initial_position:
                print('%s : %f' % (k,v-initial_position[k]))
            else:
                print('%s : %f' % (k,v))

    def gather_data(self, filepath=None, sleep=1, duration=60, maxdepth=6): # for saving market data
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
        self.trading_enabled = False
        # generate a filename if one is not provided
        if filepath is None:
            t =  "%s__%s_%s.p" % (time.strftime('%b-%d-%Y_%H-%M-%S'), sleep, duration)
            filepath = self.data_path + '/' + t

        start = time.time()
        data = {'start' : start, 'ticks' : [], 'duration' : duration, 'sleep' : sleep, 'maxdepth' : maxdepth}
        data['tradeable_pairs'] = {broker.xchg.name : broker.xchg.tradeable_pairs for broker in self.brokers}
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
                    brokerdata[market] = {'bids' : d['bids'][:maxdepth-1],
                                          'asks': d['asks'][:maxdepth-1]}
                marketdata[name] = brokerdata
            data['ticks'].append(marketdata)
            last_tick = time.time()
            pickle.dump(data, open(filepath, 'wb')) # write to file
        self.trading_enabled = False

    def trade_pair(self, pair):
        pass

    def tick(self):
        self.log.info('tick')
        for broker in self.brokers:
            # clear data so that if API call fails, we don't mistakenly
            # report last tick's data
            broker.clear()
        for pair in self.config.PAIRS:
            #print('fetching xchg data for %s' % (pair,))
            # multithreaded update of the pair on each exchange
            if self.config.USE_MULTITHREADED:
                threads = []
                threadLock = threading.Lock()
                for broker in self.brokers:
                    # multithreaded update balance
                    # balance_thread = UpdateBalanceThread(broker)
                    # balance_thread.start()
                    # threads.append(balance_thread)
                    # multithreaded update depth
                    depth_thread = UpdateDepthThread(broker, pair, self.backtest_data, self.tick_i)
                    depth_thread.start()
                    threads.append(depth_thread)
                for t in threads:
                    t.join() # wait for all update threads to complete
                    #elapsed = time.time() - start
                    #print('Broker update finished in %d ms' % (elapsed * 1000))
            else:
                # single threaded update
                for broker in self.brokers:
                    #broker.balances = broker.xchg.get_all_balances()
                    #print(broker.xchg.name)
                    broker.update_all_balances()
                    if broker.xchg.get_validated_pair(pair) is not None:
                        if self.backtest_data is not None:
                            broker.update_depth(pair, self.backtest_data, self.tick_i)
                        else:
                            broker.update_depth(pair)
            # custom function for each trading bot to implement
            # the default implementation is to do nothing - useful in situations like
            # data gathering
            if self.trading_enabled:
                self.trade_pair(pair)

