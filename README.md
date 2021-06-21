[percMovements.csv](https://github.com/lachocki/WatchList-Projects/files/6689783/percMovements.csv)
# WatchList-Projects
What you'll find here is my work since roughly October of 2020 on developing and designing trading bots. Any personal information will be left out of the code and replaced with a copious amount of Xs :) I would recommend saving this file to somewhere out of reach of GitHub so any changes you make to it CAN'T be seen by others!  Below I'll walk you through how and where to replace information so you can get it running for yourself! 

But first a few things up front. The myIndication() function was my attempt at calculating RSI on my own but I was unable and not incentivized to find frequent enough data to have it work correctly. Additionally, 'import talib' gives issues to many who have issues being able to 'pip install ta-lib', it took me a while. So you can comment out all thigs associated with that function since it isn't done (myIndication(), T.csv, S.csv, import talib). Next up I use a few different .csv files to store data: Trader_Returns.csv (Where I monitor my returns for column headers reference line 1078, percMovements.csv (which stores the relative speed of an interval of trading), StockOrders.csv (is the result of pulling my orders from the Robinhood API, reference line 1035.

Next up, changing information to your own! On line 28 you'll want to change the text with in the quotes to your one time password (OTP) which Robinhood will give you once you set up Two-Factor Authentication (2FA) which the documentation for the Robinhood API can walk you through at https://robin-stocks.readthedocs.io/en/latest/quickstart.html

On line 40 replace the Xs with your phone number and make sure to include the international code +1 if you live in the U.S.

On line 53 replace the Xs with your Finnhub API key, one of which can easily be obtained at https://finnhub.io for free and its worth noting the way my algorithms are setup they are optimized to not run over Finnhub's API data pull limit.

On line 57 you'll define the path which is referenced on line 1035 to your working directory where you have a Trader_Returns.csv to monitor returns.
[percMovements.csv](https://github.com/lachocki/WatchList-Projects/files/6689781/percMovements.csv)

Lastly, on lines 54 and 55 these act as your API keys for Twilio services which will send you text messages throughout the trading process. You will have to set this up on your own but Twilio does a great job showing you how to do so! It does cost money but it's less than a penny per SMS (USD).

Once, you have all of this set, you should be good to go for this methodology!
