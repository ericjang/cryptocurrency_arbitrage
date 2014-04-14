import decimal
import unittest
import datetime
from bterapi.public import *


class TestPublic(unittest.TestCase):
    def test_constructTrade(self):
        d = {"pair": "btc_usd",
             "type": "bid",
             "price": decimal.Decimal("1.234"),
             "tid": 1,
             "amount": decimal.Decimal("3.2"),
             "date": 1368805684.878004}
        
        t = Trade(**d)
        self.assertEqual(t.pair, d.get("pair"))
        self.assertEqual(t.type, d.get("type"))
        self.assertEqual(t.price, d.get("price"))
        self.assertEqual(t.tid, d.get("tid"))
        self.assertEqual(t.amount, d.get("amount"))
        assert type(t.date) is datetime.datetime
        self.assertEqual(t.date, datetime.datetime(2013, 5, 17, 11, 48, 4, 878004))

        # check conversion of decimal dates
        d["date"] = decimal.Decimal("1368805684.878004")
        t = Trade(**d)
        assert type(t.date) is datetime.datetime
        self.assertEqual(t.date, datetime.datetime(2013, 5, 17, 11, 48, 4, 878004))

        # check conversion of integer dates
        d["date"] = 1368805684
        t = Trade(**d)
        assert type(t.date) is datetime.datetime
        self.assertEqual(t.date, datetime.datetime(2013, 5, 17, 11, 48, 4, 0))
        
        # check conversion of string dates with no fractional seconds
        d["date"] = "2013-05-17 08:48:04"
        t = Trade(**d)
        assert type(t.date) is datetime.datetime
        self.assertEqual(t.date, datetime.datetime(2013, 5, 17, 8, 48, 4, 0))

        # check conversion of string dates with fractional seconds
        d["date"] = "2013-05-17 08:48:04.878004"
        t = Trade(**d)
        assert type(t.date) is datetime.datetime
        self.assertEqual(t.date, datetime.datetime(2013, 5, 17, 8, 48, 4, 878004))
        
        # check conversion of unicode dates with no fractional seconds
        d["date"] = u"2013-05-17 08:48:04"
        t = Trade(**d)
        assert type(t.date) is datetime.datetime
        self.assertEqual(t.date, datetime.datetime(2013, 5, 17, 8, 48, 4, 0))
        
        # check conversion of string dates with fractional seconds
        d["date"] = u"2013-05-17 08:48:04.878004"
        t = Trade(**d)
        assert type(t.date) is datetime.datetime
        self.assertEqual(t.date, datetime.datetime(2013, 5, 17, 8, 48, 4, 878004))
        
if __name__ == '__main__':
    unittest.main()        
