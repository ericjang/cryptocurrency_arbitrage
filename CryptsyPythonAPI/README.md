CryptsyPythonAPI
================

API for Cryptsy.com Exchange utilizing completely built-in functions and utilities of Python 2.7.

Example Usage
-------------
Create buy order for dgc, market id 26, then cancels all orders you have for dgc
```python
import Cryptsy
Exchange = Cryptsy.Cryptsy('KEY HERE', 'SECRET HERE')
print(Exchange.createOrder(26, "Buy", 100, 0.00000001))       # Buy 100 dgc at .00000001 each
print(Exchange.cancelMarketOrders(26))                        # Cancels all orders in market 26, dgc
```



Authors Note And Contact
-------------
If you have any questions or concerns email me at matt.joseph.smith@gmail.com or skype me at scriptprodigy!

Donations ;)
-------------
Send all donations to this cryptsy trade key please! :)
7f79452abf8d345ebc8247a631dd1f1a367cb6a0
