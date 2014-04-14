import urllib
import urllib2
import json
import time
import hmac,hashlib

def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))

class Cryptsy:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret

    def post_process(self, before):
        after = before

        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))

        return after

    def api_query(self, method, req={}):
        try:
            if(method == "marketdata" or method == "orderdata" or method == "marketdatav2"):
                ret = urllib2.urlopen(urllib2.Request('http://pubapi.cryptsy.com/api.php?method=' + method))
                return json.loads(ret.read())
            elif(method == "singlemarketdata" or method == "singleorderdata"):
                ret = urllib2.urlopen(urllib2.Request('http://pubapi.cryptsy.com/api.php?method=' + method + '&marketid=' + str(req['marketid'])))
                return json.loads(ret.read())
            else:
                req['method'] = method
                req['nonce'] = int(time.time())
                post_data = urllib.urlencode(req)

                sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
                headers = {
                    'Sign': sign,
                    'Key': self.APIKey
                }

                ret = urllib2.urlopen(urllib2.Request('https://www.cryptsy.com/api', post_data, headers))
                jsonRet = json.loads(ret.read())
                return self.post_process(jsonRet)
        # modification - catch 502 Bad Gateway errors (Cryptsy's buggy API fault)
        except urllib2.HTTPError, e:
            print(e)
            print('ASGH!! FIX THE 502 ERROR in CryptsyPythonAPI!')
            return None

    def getMarketData(self):
        return self.api_query("marketdata")

    def getMarketDataV2(self):
        return self.api_query("marketdatav2")

    def getSingleMarketData(self, marketid):
        return self.api_query("singlemarketdata", {'marketid': marketid})

    def getOrderbookData(self, marketid=None):
        if(marketid == None):
            return self.api_query("orderdata")
        return self.api_query("singleorderdata", {'marketid': marketid})

    # Outputs:
    # balances_available  Array of currencies and the balances availalbe for each
    # balances_hold   Array of currencies and the amounts currently on hold for open orders
    # servertimestamp Current server timestamp
    # servertimezone  Current timezone for the server
    # serverdatetime  Current date/time on the server
    # openordercount  Count of open orders on your account
    def getInfo(self):
        return self.api_query('getinfo')


    # Outputs: Array of Active Markets
    # marketid    Integer value representing a market
    # label   Name for this market, for example: AMC/BTC
    # primary_currency_code   Primary currency code, for example: AMC
    # primary_currency_name   Primary currency name, for example: AmericanCoin
    # secondary_currency_code Secondary currency code, for example: BTC
    # secondary_currency_name Secondary currency name, for example: BitCoin
    # current_volume  24 hour trading volume in this market
    # last_trade  Last trade price for this market
    # high_trade  24 hour highest trade price in this market
    # low_trade   24 hour lowest trade price in this market
    def getMarkets(self):
        return self.api_query('getmarkets')


    # Outputs: Array of Deposits and Withdrawals on your account
    # currency    Name of currency account
    # timestamp   The timestamp the activity posted
    # datetime    The datetime the activity posted
    # timezone    Server timezone
    # type    Type of activity. (Deposit / Withdrawal)
    # address Address to which the deposit posted or Withdrawal was sent
    # amount  Amount of transaction
    def myTransactions(self):
        return self.api_query('mytransactions')


    # Inputs:
    # marketid    Market ID for which you are querying
    ##
    # Outputs: Array of last 1000 Trades for this Market, in Date Decending Order
    # datetime    Server datetime trade occurred
    # tradeprice  The price the trade occurred at
    # quantity    Quantity traded
    # total   Total value of trade (tradeprice * quantity)
    def marketTrades(self, marketid):
        return self.api_query('markettrades', {'marketid': marketid})


    # Inputs:
    # marketid    Market ID for which you are querying
    ##
    # Outputs: 2 Arrays. First array is sellorders listing current open sell orders ordered price ascending. Second array is buyorders listing current open buy orders ordered price descending.
    # sellprice   If a sell order, price which order is selling at
    # buyprice    If a buy order, price the order is buying at
    # quantity    Quantity on order
    # total   Total value of order (price * quantity)
    def marketOrders(self, marketid):
        return self.api_query('marketorders', {'marketid': marketid})


    # Inputs:
    # marketid    Market ID for which you are querying
    # limit   (optional) Limit the number of results. Default: 200
    ##
    # Outputs: Array your Trades for this Market, in Date Decending Order
    # tradeid An integer identifier for this trade
    # tradetype   Type of trade (Buy/Sell)
    # datetime    Server datetime trade occurred
    # tradeprice  The price the trade occurred at
    # quantity    Quantity traded
    # total   Total value of trade (tradeprice * quantity)
    def myTrades(self, marketid, limit=200):
        return self.api_query('mytrades', {'marketid': marketid, 'limit': limit})


    # Outputs: Array your Trades for all Markets, in Date Decending Order
    # tradeid An integer identifier for this trade
    # tradetype   Type of trade (Buy/Sell)
    # datetime    Server datetime trade occurred
    # marketid    The market in which the trade occurred
    # tradeprice  The price the trade occurred at
    # quantity    Quantity traded
    # total   Total value of trade (tradeprice * quantity)
    def allMyTrades(self):
        return self.api_query('allmytrades')


    # Inputs:
    # marketid    Market ID for which you are querying
    ##
    # Outputs: Array of your orders for this market listing your current open sell and buy orders.
    # orderid Order ID for this order
    # created Datetime the order was created
    # ordertype   Type of order (Buy/Sell)
    # price   The price per unit for this order
    # quantity    Quantity for this order
    # total   Total value of order (price * quantity)
    def myOrders(self, marketid):
        return self.api_query('myorders', {'marketid': marketid})


    # Inputs:
    # marketid    Market ID for which you are querying
    ##
    # Outputs: Array of buy and sell orders on the market representing market depth.
    # Output Format is:
    # array(
    #   'sell'=>array(
    #     array(price,quantity),
    #     array(price,quantity),
    #     ....
    #   ),
    #   'buy'=>array(
    #     array(price,quantity),
    #     array(price,quantity),
    #     ....
    #   )
    # )
    def depth(self, marketid):
        return self.api_query('depth', {'marketid': marketid})


    # Outputs: Array of all open orders for your account.
    # orderid Order ID for this order
    # marketid    The Market ID this order was created for
    # created Datetime the order was created
    # ordertype   Type of order (Buy/Sell)
    # price   The price per unit for this order
    # quantity    Quantity for this order
    # total   Total value of order (price * quantity)
    def allMyOrders(self):
        return self.api_query('allmyorders')


    # Inputs:
    # marketid    Market ID for which you are creating an order for
    # ordertype   Order type you are creating (Buy/Sell)
    # quantity    Amount of units you are buying/selling in this order
    # price   Price per unit you are buying/selling at
    ##
    # Outputs:
    # orderid If successful, the Order ID for the order which was created
    def createOrder(self, marketid, ordertype, quantity, price):
        return self.api_query('createorder', {'marketid': marketid, 'ordertype': ordertype, 'quantity': quantity, 'price': price})


    # Inputs:
    # orderid Order ID for which you would like to cancel
    ##
    # Outputs: If successful, it will return a success code.
    def cancelOrder(self, orderid):
        return self.api_query('cancelorder', {'orderid': orderid})


    # Inputs:
    # marketid    Market ID for which you would like to cancel all open orders
    ##
    # Outputs:
    # return  Array for return information on each order cancelled
    def cancelMarketOrders(self, marketid):
        return self.api_query('cancelmarketorders', {'marketid': marketid})


    # Outputs:
    # return  Array for return information on each order cancelled
    def cancelAllOrders(self):
        return self.api_query('cancelallorders')

    # Inputs:
    # ordertype   Order type you are calculating for (Buy/Sell)
    # quantity    Amount of units you are buying/selling
    # price   Price per unit you are buying/selling at
    ##
    # Outputs:
    # fee The that would be charged for provided inputs
    # net The net total with fees
    def calculateFees(self, ordertype, quantity, price):
        return self.api_query('calculatefees', {'ordertype': ordertype, 'quantity': quantity, 'price': price})


    # Inputs: (either currencyid OR currencycode required - you do not have to supply both)
    # currencyid  Currency ID for the coin you want to generate a new address for (ie. 3 = BitCoin)
    # currencycode    Currency Code for the coin you want to generate a new address for (ie. BTC = BitCoin)
    ##
    # Outputs:
    # address The new generated address
    def generateNewAddress(self, currencyid=None, currencycode=None):

        if(currencyid != None):
            req = {'currencyid': currencyid}
        elif(currencycode != None):
            req = {'currencycode': currencycode}
        else:
            return None

        return self.api_query('generatenewaddress', req)
