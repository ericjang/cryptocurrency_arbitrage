

import config
from xchg_test import xchg_test
pair = ('LTC', 'BTC')
print('Running test on pair %s' % (pair,))

''' Coins-E '''
from CoinsE import CoinsE
xchg = CoinsE(config.COINS_E_API_KEY, config.COINS_E_SECRET)
''' BTCE '''
# from BTCE import BTCE
# xchg = BTCE(config.BTCE_KEYFILE)
''' Vircurex '''
# from Vircurex import Vircurex
# xchg = Vircurex(config.VIRCUREX_USER, config.VIRCUREX_SECURITY_WORD)
''' Cryptsy '''
# from Cryptsy import Cryptsy
# xchg = Cryptsy(config.CRYPTSY_API_KEY, config.CRYPTSY_SECRET)
''' CoinEx '''
# from CoinEx import CoinEx
# xchg = CoinEx(config.COINEX_API_KEY, config.COINEX_SECRET)
''' BTER '''
# from BTER import BTER
# xchg = BTER(config.BTER_KEYFILE)
''' CRYPTO-TRADE '''
# from CryptoTrade import CryptoTrade
# xchg = CryptoTrade(config.CRYPTOTRADE_API_KEY, config.CRYPTOTRADE_SECRET)


xchg_test(xchg, pair)

# EOF
