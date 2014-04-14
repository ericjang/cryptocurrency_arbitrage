# random-ass code snippets that I might need later on

    def get_highest_bid(self, pair):
        # each broker will have already called its
        # update_price method to fetch the new rates
        base, alt = pair
        slug = base + "_" + alt
        rates = []
        bidders = []
        for broker in self.brokers:
            if broker.xchg.get_validated_pair(pair) is not None:
                rate = broker.get_highest_bid(pair)
                rates.append(rate)
                bidders.append(broker)

        hi_bid = max(rates)
        bidder = bidders[rates.index(hi_bid)]

        return (hi_bid, bidder)

    def get_lowest_ask(self, pair):
        base, alt = pair
        slug = base + "_" + alt
        rates = []
        askers = []
        for broker in self.brokers:
            if broker.xchg.get_validated_pair(pair) is not None:
                rate = broker.get_lowest_ask(pair)
                rates.append(rate)
                askers.append(broker)

        lo_ask = min(rates)
        asker = askers[rates.index(lo_ask)]
        return (lo_ask, asker)


#                         bid_depth_i = 1
#                         ask_i = 1

#                         while profit_delta > 1e-12:
#                             profit_spread = hi_bid * (1.0 - asker.xchg.trading_fee) * (1.0 - bidder.xchg.trading_fee ) - lo_ask
#                             if (bidder_base_balance < bidder_min_base_vol) or (asker_base_afford < asker_min_base_vol):
#                                 # termination condition - must stop here because we have run out of money
#                             else:



#             bid_i = 1
#             ask_i = 1
#             bids = bidder_orders[:bid_i]
#             asks = asker_orders[:ask_i]
#
#             profit_delta = self.get_profit(bidder, bids, asker, asks)
#
#             while profit_delta > 1e-12:
#                 # increase the volume (constrained by our own balance of course)
#                 bids = bidder_orders[:bid_i]
#                 asks = asker_orders[:ask_i]
#                 bid_vol =
#
#                 profit = self.get_profit(bidder, bids, asker, asks)
#                     if profit > 1e-12:
#                         success = True
#                     self.profits[b][a] = # some value here
#                 else:
#                     # trivial reject - this will be most of the cases
#                     self.profits[b][a] = None

                        # initial: size up initial bids/asks to fill until volume exceeds
                        # the min trading volume
#                         bid_i, ask_i = 1, 1
#                         while sum([b[1] for b in bidder_orders[:bid_i]]) < bidder_min_base_vol:
#                             bid_i += 1
#                         bid_vol = sum([b[1] for b in bidder_orders[:bid_i]]) # amount of base to sell

                        # must fill the base volume
#                         while sum([a[1]/a[0] for a in asker_orders[:ask_i]]) < asker_min_base_vol:
#                             ask_i += 1
#                         ask_vol = sum([a[1]/a[0] for a in asker_orders[:ask_i]])    # amount of base to buy
                        # in order to calculate profits we have to
                        # do all the order sizing right now
                        # note, after we have determined minimum sizes, it is possible we no longer turn a profit



#         # scenario 1: fix base, profit alt
#         # base's volume is limited by the amount we can give to bidder
#         # and the amount we can receive from asker
#         smaller_base, larger_base = sorted([bid_base_volume, ask_base_volume])
#         scale_base = smaller_base / larger_base
#         # scenario 2: fix alt, profit base
#         # alt's volume is limited by what we give to asker
#         # and the amount we receive from bidder
#         smaller_alt, larger_alt = sorted([bid_alt_recv, ask_alt_give])
#         scale_alt = smaller_alt / larger_alt
#
#         bids = self.scale_order_volume(bids, scale_base)
#
#         if bid_base_volume >= ask_base_volume:
#             # scale down bid volume
#             if scale_base >= scale_alt:
#                 # scale down bid's base vol
#                 new_base_vol = bid_base_volume * scale_base
#             else:
#                 # scale down bid's alt vol
#                 new_base_vol = bid_base_volume * scale_alt
#
#         else:
#             # scale down ask volume
#             if scale_base >= scale_alt:
#                 # scale down ask
#
#             else:
#                 # scale alt
#
#         profit = bid_alt_recv - ask_alt_give

        # tricky - the final bid prices we place may not indicate the full spread
        # that we actually get, since the order we submit is a 'sub-optimal' order. We
        # can only hope that the exchange partially fills our order at a better price!

                #bid_base_volume = sum([b[1] for b in bids])  # units of base to give
        #ask_base_volume = sum([a[1] for a in asks]) # units of base to buy (recv)

