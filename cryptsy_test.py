# testing the Cryptsy API

from Exchanges.Cryptsy import Cryptsy
import config

xchg = Cryptsy(config.CRYPTSY_API_KEY, config.CRYPTSY_SECRET)

pair = ('DOGE', 'BTC')
base, alt = pair

# tradeable pairs
print(xchg.tradeable_pairs)

# get highest bid
print('Highest bid for %r', pair)
bid = xchg.get_highest_bid(base, alt)
print(bid)

print('Lowest ask:')
ask = xchg.get_lowest_ask(base, alt)
print(ask)

print('Highest bid for reverse: %f' % (xchg.get_highest_bid(alt, base)))
print('Lowest ask for reverse: %f' % (xchg.get_lowest_ask(alt, base)))

print('retrieving orderbook')
book = xchg.get_depth(base, alt)
print(book)


balance = xchg.get_balance('BTC')
print('You have %f BTC in your account' % (balance))



