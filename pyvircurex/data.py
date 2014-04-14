from common import public_request


class Pair(object):
    def __init__(self, name):
        self.name = name
        self.base, self.alternate = self.name.split("_")

        self.default_params = {"base" : self.base.upper(),
                "alt" : self.alternate.upper()}

    @property
    def lowest_ask(self):
        return public_request("lowest_ask", self.default_params)

    @property
    def highest_bid(self):
        return public_request("highest_bid", self.default_params)

    @property
    def last_trade(self):
        return public_request("last_trade", self.default_params)

    @property
    def volume(self):
        return public_request("volume", self.default_params)

    @property
    def info(self):
        return public_request("info", self.default_params)

    @property
    def orderbook(self):
        return public_request("orderbook", self.default_params)

    def trades(self, since=None):
        params = self.default_params
        if since is not None:
            params["since"] = since
        return public_request("trades", params)

