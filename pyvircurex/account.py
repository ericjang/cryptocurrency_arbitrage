import random

from common import secure_request, make_token


class Account(object):
    def __init__(self, user, secret):
        self.user = user
        self.secret = secret
        self.tid = random.randint(0, 2**32)

    def balance(self, currency):
        return secure_request(self, "balance", ("currency",), (currency,))

    def balances(self):
         return secure_request(self, "balances")

    def order(self, orderid, otype):
        return secure_request(self, "order", ("orderid",), (orderid,),
                              {'otype': otype})

    def orders(self, otype):
        return secure_request(self, "orders", (), (),
                              {'otype': otype})

    def delete_order(self, orderid):
        return secure_request(self, "delete_order", ("orderid",), (orderid,))

    def buy(self, base, amount, alternate, price):
        return secure_request(self, "create_order", \
                ("ordertype", "amount", "currency1", "unitprice", "currency2"), \
                ("BUY", amount, base, price, alternate))

    def sell(self, base, amount, alternate, price):
        return secure_request(self, "create_order", \
                ("ordertype", "amount", "currency1", "unitprice", "currency2"), \
                ("SELL", amount, base, price, alternate))

    def release_order(self, orderid):
        return secure_request(self, "release_order", ("orderid",), (orderid,))

    # new api calls for 'create_released_order'
    def quick_buy(self, base, amount, alternate, price):
        return secure_request(self, "create_released_order", \
                ("ordertype", "amount", "currency1", "unitprice", "currency2"), \
                ("BUY", amount, base, price, alternate))

    def quick_sell(self, base, amount, alternate, price):
        return secure_request(self, "create_released_order", \
                ("ordertype", "amount", "currency1", "unitprice", "currency2"), \
                ("SELL", amount, base, price, alternate))
