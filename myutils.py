
from order import Order
import copy

def get_swapped_order(order):
    # given a bid/ask price and volume being bought/sold,
    # return the same order but as units of the reverse market.
    c = copy.copy(order)
    alts_per_base = c.p
    vol_base = c.v
    c.v = vol_base * alts_per_base
    c.p = 1.0/alts_per_base
    return c
