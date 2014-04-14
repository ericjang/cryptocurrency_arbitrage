# implements API access to cryptostocks.com

# https://cryptostocks.com/api

class CryptoStocksAPI(object):
    def __init__(self,api_key,api_secret):
        self.format = 'json'.lower()
        self.api_url = 'https://cryptostocks.com/api/'
        self.api_headers = {'Content-type' : 'application/json',
                            'Accept' : 'application/json',
                            'User-Agent' : 'autocoin-autosell'}
        self.api_key = api_key
        self.api_secret = api_secret.encode('utf-8')

        self.account = "" # your email here
        self.id = 0 # this is the nonce


    # PUBLIC API
    def get_security_info(self):
        pass

    def get_securities_info(self):
        pass

    def get_list_of_securities(self):
        pass

    def get_dividend_for_security(self):
        pass

    def get_orderbook(self):
        pass

    def get_history_last_50(self):
        pass


    # TRADING API
    def get_coin_balances(self):
        pass

    def get_share_balances(self):
        pass

    def create_order(self,ticker,quantity,unitprice,validtill,ordertype):
        pass

    def read_order(self,ordernumber):
        pass

    def read_orders(self):
        pass

    def delete_order(self,ordernumber):
        pass
