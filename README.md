# WatchList-Trader3
First off this is my first use of Github so if you have advice, I'm always happy to learn. What you'll find here is my work since roughly October of 2020 on developing, designing, and refining this trading bot. It is designed to trade in any market conditions by utilizing 3x leveraged ETNs that have both a 'Bull' and 'Bear' version so you can bet for or against the market at any given point in time.

Any personal information will be left out of the code and replaced with a copious amount of Xs :) I would recommend saving this file to somewhere out of reach of GitHub so any changes you make to it CAN'T be seen by others! I think that's how that works. Below I'll walk you through how and where to replace information so you can get it running for yourself! But first.

Install & Dependencies:
Below are the 3 packages that are somewhat unusual  that the algorithm needs to be able to place trades, get data, and send SMS notifications. Otherwise most packages you'll see are pretty ordinary (os,time,pandas,etc.) Note that this algorithm is made for trading on a RobinHood brokerage account. within the Robin-Stocks module you can use it for other brokers but this one is strictly set up for RobinHood. 

pip install robin-stocks

pip install finnhub-python

pip install twilio

Next up I use a few different .csv files to store data: Trader_Returns.csv (Where I monitor my returns for column headers reference line 1078, percMovements.csv (which stores the relative speed of an interval of trading AND is attached to this so you dont have to run all of your own data), StockOrders.csv (is the result of pulling my orders from the Robinhood API, reference line 1035.

Next up, changing information to your own! On line 28 you'll want to change the text with in the quotes to your one time password (OTP) which Robinhood will give you once you set up Two-Factor Authentication (2FA) which the documentation for the Robinhood API can walk you through at https://robin-stocks.readthedocs.io/en/latest/quickstart.html

On line 40 replace the Xs with your phone number and make sure to include the international code +1 if you live in the U.S.

On line 53 replace the Xs with your Finnhub API key, one of which can easily be obtained at https://finnhub.io for free and its worth noting the way my algorithms are setup they are optimized to not run over Finnhub's API data pull limit.

On line 57 you'll define the path which is referenced on line 1035 to your working directory where you have a Trader_Returns.csv to monitor returns.

On lines 54 and 55 these act as your API keys for Twilio services which will send you text messages throughout the trading process. You will have to set this up on your own but Twilio does a great job showing you how to do so! It does cost money but it's less than a penny per SMS (USD). Once you have these keys enter them as environmental variables for added security.

Lastly, on line 62 you can change 'overall_percent' to your liking. It controls how much of your available account cash you want to use for a given trade.

Once, you have all of this set, you should be good to go for this methodology!
