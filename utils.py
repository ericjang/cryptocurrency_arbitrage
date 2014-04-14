
highest_price = lambda arr : max([o.v for o in arr])
lowest_price = lambda arr : min([o.v for o in arr])
total_base_volume = lambda arr : sum([o.v for o in arr])
total_alt_volume = lambda arr : sum([o.p * o.v for o in arr])