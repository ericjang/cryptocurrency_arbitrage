import exchange_api
import hashlib
import hmac
import json
try:
    import http.client
    import urllib.request
    import urllib.error
except ImportError:
    # Python 2.7 compatbility
    import httplib
    class http: client = httplib
    import urllib2
    class urllib: request = urllib2; error = urllib2

class CoinEx(exchange_api.Exchange):

    name = 'CoinEx'

    def __init__(self, api_key, api_secret):
        self.api_url = 'https://coinex.pw/api/v2/'
        self.api_headers = {'Content-type' : 'application/json',
                            'Accept' : 'application/json',
                            'User-Agent' : 'autocoin-autosell'}
        self.api_key = api_key
        self.api_secret = api_secret.encode('utf-8')

    def GetName(self):
        return 'CoinEx'

    def _Request(self, method, headers=None, post_data=None, json_root=None):
        if headers is None:
            headers = {}
        headers.update(self.api_headers.items())
        try:
            request = urllib.request.Request(self.api_url + method, post_data, headers)
            response = urllib.request.urlopen(request)
            try:
                response_json = json.loads(response.read().decode('utf-8'))
                if not json_root:
                    json_root = method
                if not json_root in response_json:
                    raise exchange_api.ExchangeException('JSON root "%s" not in "%s".' %
                                                         (json_root, method))
                return response_json[json_root]
            finally:
                response.close()
        except (urllib.error.URLError, urllib.error.HTTPError, http.client.HTTPException,
                ValueError) as e:
            raise exchange_api.ExchangeException(e)

    def _PrivateRequest(self, method, post_data=None, json_root=None):
        hmac_data = b'' if not post_data else post_data
        digest = hmac.new(self.api_secret, hmac_data, hashlib.sha512).hexdigest()
        headers = {'API-Key' : self.api_key,
                   'API-Sign': digest}
        return self._Request(method, headers, post_data, json_root)

    def GetCurrencies(self):
        try:
            return {currency['id'] : str(currency['name']) for
                    currency in self._Request('currencies')}
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)

    def GetBalances(self):
        balances = {}
        try:
            for balance in self._PrivateRequest('balances'):
                balances[balance['currency_id']] = float(balance['amount']) / pow(10, 8)
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)
        return balances

    def GetMarkets(self):
        try:
            return [exchange_api.Market(trade_pair['currency_id'], trade_pair['market_id'],
                                        trade_pair['id']) for
                    trade_pair in self._Request('trade_pairs')]
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)

    def CreateOrder(self, market_id, amount, bid=True, price=0):
        order = {'trade_pair_id' : market_id,
                 'amount' : int(amount * pow(10, 8)),
                 'bid' : bid,
                 'rate' : max(1, int(price * pow(10, 8)))}
        post_data = json.dumps({'order' : order}).encode('utf-8')
        try:
            return self._PrivateRequest('orders', post_data, 'order')['id']
        except (TypeError, KeyError, IndexError) as e:
            raise exchange_api.ExchangeException(e)