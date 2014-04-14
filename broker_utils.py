
from Broker import Broker

# exchanges
import config
from BTCE import BTCE
from Cryptsy import Cryptsy
from BTER import BTER
from CoinEx import CoinEx
from CoinsE import CoinsE
from Vircurex import Vircurex
from CryptoTrade import CryptoTrade

def create_brokers(mode, pairs, exchangeNames):
    # returns an array of Broker objects
    brokers = []
    for name in exchangeNames:
        if (name == 'VIRCUREX'):
            xchg = Vircurex(config.VIRCUREX_USER, config.VIRCUREX_SECURITY_WORD)
        elif (name == 'BTCE'):
            xchg = BTCE(config.BTCE_KEYFILE)
        elif (name == 'BTER'):
            xchg = BTER(config.BTER_KEYFILE)
        elif (name == 'COINS-E'):
            xchg = CoinsE(config.COINS_E_API_KEY, config.COINS_E_SECRET)
        elif (name == 'CRYPTSY'):
            xchg = Cryptsy(config.CRYPTSY_API_KEY, config.CRYPTSY_SECRET)
        elif (name == 'CRYPTO-TRADE'):
            xchg = CryptoTrade(config.CRYPTOTRADE_API_KEY, config.CRYPTOTRADE_SECRET)
        elif (name == 'COINEX'):
            xchg = CoinEx(config.COINEX_API_KEY, config.COINEX_SECRET)
        else:
            print('Exchange ' + name + ' not supported!')
            continue
        print('%s initialized' % (xchg.name))

        broker = Broker(mode, xchg)
        if mode == 'BACKTEST':
#            broker.balances = config.PAPER_BALANCE
            broker.balances = broker.xchg.get_all_balances() # use real starting balances.
        brokers.append(broker)
    return brokers

def get_assets(brokers):
    # prints out total assets held across all brokers
    assets = {}
    for broker in brokers:
        for currency, balance in broker.balances.items():
            if currency in assets:
                assets[currency] += balance
            elif balance > 0.0:
                assets[currency] = balance
    return assets

def print_assets(brokers):
    print(get_assets(brokers))
