cryptocurrency_arbitrage
========================

A million dollars isn't cool. You know what's cool? 

A BILLION DOLLARS

This is an automated trading program that detects pairwise and triangular arbitrage opportunities on altcoin/bitcoin exchanges. Compared to other bots out there, this one is fairly high-frequency (can trade up to once every 30 seconds or so). 

This one handles a lot of the nasty market microstructure calculations like order volume sizing in illiquid orderbooks, transaction fees, situations where an orderbook is reversed, etc. It is easily extendible to support more exchanges and strategies.

## Is it profitable?

I have made some money off of it, so yes. But automated order submission and confirmation have not been implemented.

## Why are you giving it away for free?

- With HFT bots, one has to be really careful with order confirmation - otherwise you could lose all your money in a matter of minutes if an exchange goes invsolvent or something. I wouldn't sleep well at night if I were running a scalping operation on my own.

- I am of the opinion that the success of Bitcoin and altcoins are mutually exclusive and it is unwise to maintain sizeable positions in currencies that could become illiquid/unwanted very soon. I'd much rather put my money into passive investing, which takes considerably less work than trading.

- That said, it's a grand shame to leave this code unused on my computer so I've put it up online for educational purposes. Designing and implementing this has taught me so much about financial markets and Bitcoin and that is a reward in its own right.

## How do I use it?

Warning: I am not responsible for any losses you incur using this program. You should not run this without looking at the source code for the entire program and running the paper trading/backtesting framework first.

This program comes with two strategies. The first one is pairwise arbitrage, in which the price difference between a currency pair A_B between two different exchanges is exploited via instantaneous arbitrage (to circumvent 2 hour delay in blockchain confirmation). The nice thing about trading altcoins with altcoins is that you don't have to muck around (yet) with financial regulation or set up brokerage accounts or deal with exorbitant fiat withdrawal fees from the small number of exchanges who support it (of which the bid-ask spread is low anyway).

Run one of the following scripts:

```main_pair.py``` - runs real-time paper or live trading.

```main_pair_data.py``` - gathers and caches live market depths to be played back for backtesting

```main_pair_backtest.py``` - runs backtest of trading strategies on gathered data

The second strategy is triangular arbitrage. It is nice because it can often be carried out on one exchange (i.e. such as CoinEx) and thus circumvents the time taken for blockchain confirmation (i.e. you can use new securities immediately).

The equivalent scripts are ```main_tri.py```, ```main_tri_data.py```, and ```main_tri_backtest.py```, respectively.

Put your secret keys in ```config.py```. Keep those safe.

## Is there any documentation?

My code is sprinkled with liberal amounts of comments, for better or worse.

## Credits

Some exchange access APIs included in this source code were not implemented by me. 

If you find this program useful and would like to donate, I accept Bitcoin and Dogecoin! 

BTC: 1MLX2kMhTSRiq3Uz7R2JsECreuQEmofQy6

DOGE: DE57RJrW9Qmq6pKXSTViP8QVmu63FxfHbM