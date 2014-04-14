import time # for profiling how long each test takes

def get_highest_bid(orderbook, pair):
    # orderbook = dictionary containing array of 'bids' and 'asks'
    orderbook['bids'].sort(key=lambda x: x[0], reverse=True)
    return orderbook['bids'][0]

def get_lowest_ask(orderbook, pair):
    orderbook['asks'].sort(key=lambda x: x[0], reverse=False)
    return orderbook['asks'][0]

def xchg_test(xchg, pair):
    start = time.time()
    # performs tests on the essential exchange features
    print('Testing Exchange : %s ' % (xchg.name))
    base, alt = pair
    print('Tradeable Pairs:')
    print(xchg.tradeable_pairs)
    print('Retrieving Orderbook:')
    book = xchg.get_depth(base, alt)
    print(book)
    bid = get_highest_bid(book, pair)
    print('Highest Bid: %s' % (bid,))
    ask = get_lowest_ask(book, pair)
    print('Lowest Ask: %s' % (ask,))
    if bid[0] > ask[0]:
        print('Warning! Bid should not be larger than ask!')
    # repeat with opposite pair
#    p = (alt, base)
#    bid = get_highest_bid(book, p)
#     print('Highest Bid for reverse spread: %s' % (bid,))
#     ask = get_lowest_ask(book, p)
#     print('Lowest ask for reverse: %s' % (ask,))
    balance = xchg.get_balance('BTC')
    print('You have %f BTC in your account' % (balance))
    elapsed = time.time() - start
    print('Test finished in %d ms' % (elapsed * 1000))
    # TODO: submit a tiny unfillable order, then monitor it

def bad_order():
    # submit order for currencies that I don't have money for
    # this is just in case I accidentally sell away all my assets
    # for a low price
    return NotImplemented