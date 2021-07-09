#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 13:43:33 2021
CONFIDENTIAL
@author: michaellachocki
"""


import robin_stocks.robinhood as r
import finnhub
import requests
from twilio.rest import Client
import os
import datetime
from datetime import datetime
import time
import pandas as pd
import numpy as np
import pyotp
#import talib
import traceback

username = os.getenv("Username")
password = os.getenv("Password")

def login():
    totp  = pyotp.TOTP("XXXXXXXXXXXXXXXX").now()
    login = r.login(username,password,mfa_code=totp)
    
login()

nl="\n"
short=5
UpperLimit=60
LowerLimit=25
totalbuys=0
rr=1
exc=0
mpn="+1XXXXXXXXXX"
attempts=0
done=False
lowestT=100
lowestS=100
prices=[]
buy=False
boughtLL=100
boughtWhen='0000'
bought=False
profitSell=0.10
IntraDayBuys=[]
BuyPrice=float()
finnhub_client = finnhub.Client(api_key="XXXXXXXXXXXXXXXXXXXXXX")
account_sid = os.getenv("TWILIO-ACCOUNT-SID")
auth_token = os.getenv("TWILIO-AUTH-TOKEN")
client = Client(account_sid, auth_token)
path='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'#Example /Users/michaellachocki/Desktop
pullInterval=15
numM=6
buyMessage='Beginning Buy Process'
sellMessage='Beginning Sell Process'
overall_percent=0.20
stopNum=0

def getPrice(ticker):
    login()
    CurrentQuote=r.stocks.get_stock_quote_by_symbol(ticker, info=None)
    TradingPrice=round(float(CurrentQuote['last_trade_price']),2)
    return TradingPrice

def howMany(ticker,overall_percent):
    login()
    cash=r.profiles.load_account_profile(info='portfolio_cash')
    print("Cash Balance $",cash,nl)
    HowMuch=float(float(cash)*overall_percent)
    
    if ticker==T:
        TradingPrice=getPrice(T)
        PtQ=round(HowMuch/TradingPrice,2)
        PtQ2=int(round(HowMuch/TradingPrice,-1))
        print("$",HowMuch,"can buy you",PtQ,"shares of",tt,nl,"Rounding to",PtQ2,"shares.",nl)
        HowManyT=PtQ2  
        return HowManyT

    TradingPrice=getPrice(S)
    PtQ=round(HowMuch/TradingPrice,2)
    PtQ2=int(round(HowMuch/TradingPrice,-2))
    print("$",HowMuch,"can buy you",PtQ,"shares of",ss,nl,"Rounding to",PtQ2,"shares.",nl)
    HowManyS=PtQ2 
    return HowManyS
    
def ladder():
    #QQQ Indication Level Ladder
    login()
    TodayOpen=float(r.stocks.get_fundamentals('QQQ', info='open')[0])
    QQQQuote=r.stocks.get_stock_quote_by_symbol('QQQ', info=None)
    TradingPrice=round(float(QQQQuote['last_trade_price']),2)
    QQQFromOpen=((TradingPrice-TodayOpen)/TodayOpen)
    QQQChange= ((TradingPrice-float(QQQQuote['previous_close']))/float(QQQQuote['previous_close']))
    
    if QQQChange >= 0.01 or QQQChange <= -0.01 or QQQFromOpen >= 0.015 or QQQFromOpen <=-0.015:
        UpperLimit=55
        LowerLimit=18
        stopPerc= -0.00325
    elif QQQChange >= 0.009 or QQQChange <= -0.009 or QQQFromOpen >= 0.0135 or QQQFromOpen <=-0.0135:
        UpperLimit=55
        LowerLimit=19
        stopPerc= -0.003
    elif QQQChange >= 0.008 or QQQChange <= -0.008 or QQQFromOpen >= 0.012 or QQQFromOpen <=-0.012:
        UpperLimit=55
        LowerLimit=20
        stopPerc= -0.003
    elif QQQChange >= 0.007 or QQQChange <= -0.007 or QQQFromOpen >= 0.0105 or QQQFromOpen <=-0.0105:
        UpperLimit=55
        LowerLimit=21
        stopPerc= -0.003
    elif QQQChange >= 0.006 or QQQChange <= -0.006 or QQQFromOpen >= 0.009 or QQQFromOpen <=-0.009:
        UpperLimit=55
        LowerLimit=22
        stopPerc= -0.00275
    elif QQQChange >= 0.005 or QQQChange <= -0.005 or QQQFromOpen >= 0.0075 or QQQFromOpen <=-0.0075:
        UpperLimit=55
        LowerLimit=23
        stopPerc= -0.00275
    elif QQQChange >= 0.004 or QQQChange <= -0.004 or QQQFromOpen >= 0.006 or QQQFromOpen <=-0.006:
        UpperLimit=55
        LowerLimit=24
        stopPerc= -0.00275
    else:
        UpperLimit=55
        LowerLimit=25
        stopPerc= -0.00275
        
    return UpperLimit, LowerLimit, stopPerc

def indication(ticker,shorthand,HowManyT,HowManyS):
    
    UpperLimit,LowerLimit,stopPerc=ladder()
    
    if ticker == T:
        howmany=HowManyT
    elif ticker == S:
        howmany=HowManyS
        
    datapull=finnhub_client.technical_indicator(symbol=ticker, resolution='1', _from=int(time.time()-864000), to=int(time.time()), indicator='rsi',indicator_fields={"timeperiod": 14})
    rsis=datapull['rsi']
    ts=datapull['t']
    df=pd.DataFrame()
    df["RSI"]=rsis
    df["Unix_TS"]=ts
    cut=df.tail(1)
    rsi=int(cut["RSI"])
    print(datetime.fromtimestamp(cut["Unix_TS"]),"|",shorthand,": Indication->",rsi,"(",LowerLimit,"-",UpperLimit,")",howmany)
    return rsi

def stoploss(ticker,shorthand,BuyPrice,stopPerc,HowMany):
    import numpy as np
    TradingPrice=getPrice(ticker)
    print('Price:',TradingPrice,nl)
    if round(((TradingPrice-BuyPrice)/BuyPrice),5) < stopPerc:
        stopPrices=[]
        print("Price to Beat:",TradingPrice)
        for i in range(0,10):
            newPrice=getPrice(ticker)
            print("New Price:",newPrice)
            time.sleep(1)
            stopPrices.append(newPrice)
        avgPrice= round(np.average(stopPrices),2)
        print("Average of last 10 prices:",avgPrice,nl)
        if avgPrice >= TradingPrice:
            print("Price not falling reliably.",nl)
            pass
        else:
            login()
            sell_order=r.orders.order_sell_market(ticker, HowMany, timeInForce='gfd', extendedHours=False)
            print("Selling",shorthand,"for an approx.",stopPerc,"% loss")
        
            message = client.messages \
                            .create(
                                  body="Selling "+shorthand+" for an approx. "+str(round(stopPerc*100,3))+"% loss",
                                  from_='+12564748541',
                                  to=mpn
                              )
            print(message.sid)
            IntraDayBuys.remove(ticker)
            return sell_order             
    pass
    
def cancelOrder(ticker,shorthand,order,side):
    attempts=0
    done=False
    while True:
        login()
        order=r.orders.get_stock_order_info(order['id'])
        if order['state'] == 'filled':
            break
        
        attempts+=1
        print(datetime.now().strftime('%H%M%S'))
        time.sleep(1)
        
        if attempts > 20:
            login()
            try:
                r.orders.cancel_stock_order(order['id'])
                done=True
        
                message = client.messages \
                                .create(
                                      body="Order for "+shorthand+" has been cancelled, time allowance surpassed.",
                                      from_='+12564748541',
                                      to=mpn
                                  )
                print(message.sid)
                done= fakeCancel(T,S,side)
                break
            
            except Exception as e:
                print(e)
                done= fakeCancel(T,S,side)
                break
                
            
    return done, order

def phase3(ticker,shorthand,nowPrice,pullInterval,numM):
    weight=[0.05,0.05,0.1,0.2,0.2,0.2]
    print("Entering Phase 3 of the Buy Process")
    tickSpeed(ticker)
    print("Price to beat $",nowPrice,nl)
    while True:
        time.sleep(pullInterval)
        login()
        newPrice=getPrice(ticker)
        print("New Price $",newPrice,nl)
        prices.append(newPrice)
        if len(prices) == numM:
            avgPrice=round(np.average(prices,weights=weight),2)
            print("Weighted average of the",numM,"prices in the last",pullInterval*numM,"seconds $",avgPrice,nl)
            prices.clear()
            if avgPrice <= nowPrice:
                nowPrice=avgPrice
                print("Price Still Falling",nl)
                continue
            else:
                break
            
    return nowPrice
   
def phase3sell(ticker,shorthand,nowPrice,pullInterval,numM):
    weight=[0.05,0.05,0.1,0.2,0.2,0.2]
    print("Entering Phase 3 of the Sell Process")
    tickSpeed(ticker)
    print("Price to beat $",nowPrice,nl)
    while True:
        time.sleep(pullInterval)
        login()
        newPrice=getPrice(ticker)
        print("New Price $",newPrice,nl)
        prices.append(newPrice)
        if len(prices) == numM:
            avgPrice=round(np.average(prices,weights=weight),2)
            print("Weighted average of the",numM,"prices in the last",pullInterval*numM,"seconds $",avgPrice,nl)
            prices.clear()
            if avgPrice >= nowPrice:
                nowPrice=avgPrice
                print("Price Still Rising",nl)
                continue
            else:
                break  

def notifyMe(message,shorthand):
    message = client.messages \
                .create(
                      body=message+" on "+shorthand,
                      from_='+12564748541',
                      to=mpn
                  )
    print(message.sid) 

def sellProcess(ticker,shorthand,HowMany):

    notifyMe(sellMessage,shorthand)
    print("Beginning Sell Process on",shorthand,nl)
    login()
    nowPrice=getPrice(ticker)
    phase3sell(ticker,shorthand,nowPrice,pullInterval,numM)
    login()
    sell_order=r.orders.order_sell_market(ticker, HowMany, timeInForce='gfd', extendedHours=False)
    print("Selling: ",HowMany,"shares of",shorthand,nl)
    done, sell_order= cancelOrder(ticker, shorthand, sell_order,'sell')
    if done:
        while True:
            time.sleep(2)
            login()
            sell_order=r.orders.order_sell_market(ticker, HowMany, timeInForce='gfd', extendedHours=False)
            done,sell_order=cancelOrder(ticker, shorthand, sell_order,'sell')
            if done:
                continue
            else:
                break

    SellPrice=round(float(sell_order['price']),2)

    message = client.messages \
                    .create(
                          body="Sold "+str(HowMany)+" "+shorthand+" for $"+str(SellPrice)+": Indication > "+str(UpperLimit),
                          from_='+12564748541',
                          to=mpn
                      )
    print(message.sid)

    IntraDayBuys.remove(ticker)
    return SellPrice

def What():
    print(nl,"For T&S enter '1' OR for FS&FZ enter '2':")
    option=int(input())
    if option == 1:
        T="TQQQ"
        S="SQQQ"
        tt="T"
        ss="S"
        return T,S,tt,ss
    elif option == 2:
        T="FAS"
        S="FAZ"
        tt="FS"
        ss="FZ"
        return T,S,tt,ss
    else:
        print("Neither 1 or 2 entered. Reverting to default.",nl)
        T="TQQQ"
        S="SQQQ"
        tt="T"
        ss="S"
        return T,S,tt,ss
  
def fakeCancel(T,S,side):
    login()
    positions=r.account.build_holdings(with_dividends=False)
    if side == 'buy':
        if len(positions) == 0:
            print("Cancel Successful",nl)
            
        elif T in positions:
            print("Filled or partially filled T order",nl)
            done=False
            return done
            
            
        elif S in positions:
            print("Filled or partially filled S order",nl)
            done=False
            return done
            
        else:
            print("Something else is owned. Not to worry.",nl)
            
    elif side == 'sell':
        if len(positions) == 0:
            print("Sell went through, cancel unsuccessful",nl)
            
        elif T in positions:
            print("Cancel T Successful",nl)
            done=True
            return done
            
            
        elif S in positions:
            print("Cancel S Successful",nl)
            done=True
            return done
            
        else:
            print("Something else is owned. Not to worry.",nl)
    
def tickSpeed(ticker):
    from statistics import stdev
    prices=[]
    print("Figuring Tick Speed")
    for i in range(0,11):
        if i == 0:
            oldPrice=getPrice(ticker)
            time.sleep(1)
        else:
            newPrice=getPrice(ticker)
            priceChng=abs(newPrice-oldPrice)
            print("$",newPrice,'-',oldPrice,'=',priceChng)
            prices.append(priceChng)
            oldPrice=newPrice
            time.sleep(1)
            
    sumMovements=sum(prices)
    print("Sum of movements:",sumMovements)
    newPrice=getPrice(ticker)
    percMovements=sumMovements/newPrice
    print("sumMovements/newPrice",percMovements,nl)
    # tickLadder(percMovements)
    
    tickData = pd.read_csv("percMovements.csv", encoding='latin-1',index_col=[0])
    new_row={'percMovements':percMovements}
    tickData=tickData.append(new_row, ignore_index=True)
    tickData.to_csv("percMovements.csv")
    #Ladder
    avgM=tickData['percMovements'].mean()
    stdM=stdev(tickData['percMovements'])
    if 0 <= percMovements < (avgM-stdM):
        pullInterval=12
    elif (avgM-stdM) <= percMovements < avgM:
        pullInterval=10
    elif avgM <= percMovements < (avgM+stdM):
        pullInterval=8
    elif (avgM+stdM) <= percMovements < avgM+(2*stdM):
        pullInterval=6
    elif avgM+(2*stdM) <= percMovements:
        pullInterval=4
        
    print("PI =",pullInterval,nl)
    return pullInterval

T,S,tt,ss=What()
HowManyT=howMany(T,overall_percent)
HowManyS=howMany(S,overall_percent)

while True:
    now = datetime.now().strftime('%H%M')
    weekno = datetime.today().weekday()
    time.sleep(short)

    if '0730' <= now <= '1345' and weekno < 5:#My local time for U.S. Trading Hours
        rr=0
        try:
            UpperLimit,LowerLimit,stopPerc=ladder()
                
            #Current RSI T  
            CurrentRSIT=indication(T,tt,HowManyT,HowManyS)
            if CurrentRSIT < lowestT:
                lowestT=CurrentRSIT
                occtimeT=now
            
            #Current RSI S
            CurrentRSIS=indication(S,ss,HowManyT,HowManyS)
            if CurrentRSIS < lowestS:
                lowestS=CurrentRSIS
                occtimeS=now
                
            # myIndication()
            
            if bought == False:
                print(exc,"exceptions have occurred today")
                print("Lowest Indications |",tt,":",round(lowestT,1),"at",occtimeT,ss,":",round(lowestS,1),"at",occtimeS)
            if bought==True:
                print(exc,"exceptions have occurred today")
                print("Lowest Indications |",tt,":",round(lowestT,1),"at",occtimeT,ss,":",round(lowestS,1),"at",occtimeS)
                print("Bought Initiated at",boughtWhen,"when LL ==",boughtLL)
            
############BUY T
            if CurrentRSIT < LowerLimit and len(IntraDayBuys) == 0 and now < '1300':
                notifyMe(buyMessage,tt)
                if now >= '1230' and HowManyT > 200:
                    HowManyT=int(HowManyT*0.05)
                    
                print("Beginning Buy Process on",tt,nl)
                boughtWhen=now
                boughtLL=LowerLimit
                while True:
                    try:
                        time.sleep(short)
                        CurrentRSIT=indication(T,tt,HowManyT,HowManyS)

                        if CurrentRSIT > 25:
                            nowPrice=getPrice(T)
                            nowPrice=phase3(T,tt,nowPrice,pullInterval,numM)
                            while True:
                                try:
                                    CurrentRSIT=indication(T,tt,HowManyT,HowManyS)
                                    break
                                except Exception:
                                    traceback.print_exc()
                                    continue
                                
                            if CurrentRSIT > 25:
                                break

                            else:
                                continue
                            
                        elif CurrentRSIT <= 25:
                            continue                
                        
                    except Exception:
                        traceback.print_exc()
                        continue
                
                login()
                buy_order=r.orders.order_buy_market(T, HowManyT,timeInForce='gfd', extendedHours=False)
                print("Buyng: ",HowManyT,"shares of",tt,nl)
                done, buy_order=cancelOrder(T, tt, buy_order,'buy')

                if done:
                    while True:
                        phase3(T,tt,nowPrice,2,6)
                        login()
                        buy_order=r.orders.order_buy_market(T, HowManyT,timeInForce='gfd', extendedHours=False)
                        print("Buyng: ",HowManyT,"shares of",tt,nl)
                        done, buy_order=cancelOrder(T, tt, buy_order,'buy')
                        if done: 
                            continue
                        else:
                            break
                
                else:
                    pass
                buy_order=r.orders.get_stock_order_info(buy_order['id'])
                HowManyT=round(float(buy_order['quantity']))
                BuyPrice=round(float(buy_order['price']),2)

                message = client.messages \
                                .create(
                                      body="Bought "+str(HowManyT)+" "+tt+" at $"+str(BuyPrice)+ " Indication > "+str(LowerLimit),
                                      from_='+12564748541',
                                      to=mpn
                                  )
                print(message.sid)
                
                IntraDayBuys.append(T)
                bought=True
                time.sleep(short)
                
                print("Beginning to watch price for a turn over")
                while True:
                    try:
                        CurrentRSIT=indication(T,tt,HowManyT,HowManyS)
                        CurrentPrice=getPrice(T)
                        
                        if CurrentRSIT > 55 or ((CurrentPrice-BuyPrice)/BuyPrice) >= 0.0045:
                            break
                        
                        sell_order= stoploss(T,tt,BuyPrice,stopPerc,HowManyT)
                        time.sleep(1)
                        
                        if len(IntraDayBuys) == 0:
                            stopNum+=1
                            login()
                            done,sell_order=cancelOrder(T,tt,sell_order,'sell')
                            if done:
                                while True:
                                    login()
                                    sell_order=r.orders.order_sell_market(T, HowManyT, timeInForce='gfd', extendedHours=False)
                                    done,sell_order=cancelOrder(T, tt, sell_order,'sell')
                                    if done:
                                        continue
                                    else:
                                        break

                                
                            nowPrice=getPrice(T)
                            nowPrice=phase3(T,tt,nowPrice,pullInterval,numM)
    
                            login()
                            
                            if stopNum < 2:
                                buy_order=r.orders.order_buy_market(T, HowManyT,timeInForce='gfd', extendedHours=False)
                                print("Buyng: ",HowManyT,"shares of",tt,nl)
                            else:
                                print("Stop-loss limit reached",nl)
                                stopNum=0
                                break
                                            
                            done, buy_order=cancelOrder(T, tt, buy_order,'buy')
                                            
                            if done:
                                while True:
                                    phase3(T,tt,nowPrice,2,6)
                                    login()
                                    buy_order=r.orders.order_buy_market(T, HowManyT,timeInForce='gfd', extendedHours=False)
                                    print("Buyng: ",HowManyT,"shares of",tt,nl)
                                    done, buy_order=cancelOrder(T, tt, buy_order,'buy')
                                    if done:
                                        continue
                                    else:
                                        break              
                            else:
                                pass
                            buy_order=r.orders.get_stock_order_info(buy_order['id'])
                            HowManyT=round(float(buy_order['quantity']))
                            BuyPrice=round(float(buy_order['price']),2)
            
                            message = client.messages \
                                            .create(
                                                  body="Bought "+str(HowManyT)+" "+tt+" at $"+str(BuyPrice)+ " Indication > "+str(LowerLimit),
                                                  from_='+12564748541',
                                                  to=mpn
                                              )
                            print(message.sid)
                            
                            IntraDayBuys.append(T)
                            bought=True
                            time.sleep(short)
            
                    except Exception:
                        traceback.print_exc()
                        continue
                totalbuys+=1
                continue
                    
            
#############BUY S
            if CurrentRSIS < LowerLimit and len(IntraDayBuys) == 0 and now < '1300':
                notifyMe(buyMessage,ss)
                if now >= '1230' and HowManyS > 200:
                    HowManyS=int(HowManyS*0.05)
                    
                print("Beginning Buy Process on",ss,nl)
                boughtWhen=now
                boughtLL=LowerLimit
                while True:
                    try:
                        time.sleep(short)
                        CurrentRSIS=indication(S,ss,HowManyT,HowManyS)

                        if CurrentRSIS > 25:
                            nowPrice=getPrice(S)
                            nowPrice=phase3(S,ss,nowPrice,pullInterval,numM)
                            while True:
                                try:
                                    CurrentRSIS=indication(S,ss,HowManyT,HowManyS)
                                    break
                                except Exception:
                                    traceback.print_exc()
                                    continue
                                
                            if CurrentRSIS > 25:
                                break

                            else:
                                continue
                            
                        elif CurrentRSIS <= 25:
                            continue                
                        
                    except Exception:
                        traceback.print_exc()
                        continue
                
                login()
                buy_order=r.orders.order_buy_market(S, HowManyS,timeInForce='gfd', extendedHours=False)
                print("Buyng: ",HowManyS,"shares of",ss,nl)
                done, buy_order=cancelOrder(S, ss, buy_order,'buy')

                
                if done:
                    while True:
                        phase3(S,ss,nowPrice,2,6)
                        login()
                        buy_order=r.orders.order_buy_market(S, HowManyS,timeInForce='gfd', extendedHours=False)
                        print("Buyng: ",HowManyS,"shares of",ss,nl)
                        done, buy_order=cancelOrder(S, ss, buy_order,'buy')
                        if done: 
                            continue
                        else:
                            break
                
                else:
                    pass
                
                buy_order=r.orders.get_stock_order_info(buy_order['id'])
                HowManyS=round(float(buy_order['quantity']))
                BuyPrice=round(float(buy_order['price']),2)

                message = client.messages \
                                .create(
                                      body="Bought "+str(HowManyS)+" "+ss+" at $"+str(BuyPrice)+ " Indication > "+str(LowerLimit),
                                      from_='+12564748541',
                                      to=mpn
                                  )
                print(message.sid)
                
                IntraDayBuys.append(S)
                bought=True
                time.sleep(short)
                
                print("Beginning to watch price for a turn over")
                while True:
                    try:
                        CurrentRSIS=indication(S,ss,HowManyT,HowManyS)
                        CurrentPrice=getPrice(S)
                        
                        if CurrentRSIS > 55 or ((CurrentPrice-BuyPrice)/BuyPrice) >= 0.0045:
                            break
                        
                        sell_order=stoploss(S,ss,BuyPrice,stopPerc,HowManyS)
                        time.sleep(1)
                        
                        if len(IntraDayBuys) == 0:
                            stopNum+=1
                            login()
                            done,sell_order=cancelOrder(S,ss,sell_order,'sell')
                            if done:
                                while True:
                                    login()
                                    sell_order=r.orders.order_sell_market(S, HowManyS, timeInForce='gfd', extendedHours=False)
                                    done,sell_order=cancelOrder(S, ss, sell_order,'sell')
                                    if done:
                                        continue
                                    else:
                                        break

                                
                            nowPrice=getPrice(S)
                            nowPrice=phase3(S,ss,nowPrice,pullInterval,numM)
    
                            login()
                            if stopNum < 2:
                                buy_order=r.orders.order_buy_market(S, HowManyS,timeInForce='gfd', extendedHours=False)
                                print("Buyng: ",HowManyS,"shares of",ss,nl)
                            else:
                                print("Stop-loss limit reached",nl)
                                stopNum=0
                                break
                                            
                            done, buy_order=cancelOrder(S, ss, buy_order,'buy')
                                            
                            if done:
                                while True:
                                    phase3(S,ss,nowPrice,2,6)
                                    login()
                                    buy_order=r.orders.order_buy_market(S, HowManyS,timeInForce='gfd', extendedHours=False)
                                    print("Buyng: ",HowManyS,"shares of",ss,nl)
                                    done, buy_order=cancelOrder(S, ss, buy_order,'buy')
                                    if done:
                                        continue
                                    else:
                                        break              
                            else:
                                pass
                            
                            buy_order=r.orders.get_stock_order_info(buy_order['id'])
                            HowManyS=round(float(buy_order['quantity']))
                            BuyPrice=round(float(buy_order['price']),2)             
            
                            message = client.messages \
                                            .create(
                                                  body="Bought "+str(HowManyS)+" "+ss+" at $"+str(BuyPrice)+ " Indication > "+str(LowerLimit),
                                                  from_='+12564748541',
                                                  to=mpn
                                              )
                            print(message.sid)
                            
                            IntraDayBuys.append(S)
                            bought=True
                            time.sleep(short)
            
                    except Exception:
                        traceback.print_exc()
                        continue
                totalbuys+=1
                continue

#############T Owned or Trailing-Stop
            if CurrentRSIT < UpperLimit and len(IntraDayBuys) > 0 and IntraDayBuys[0]==T:
                
                if CurrentRSIT < LowerLimit:
                    print(tt,"is already owned",nl)
                    pass
                
                elif CurrentRSIT > LowerLimit:
                    SellPrice=sellProcess(T,tt,HowManyT)
                    if SellPrice > BuyPrice:
                        HowManyT= int(HowManyT*profitSell)
                        HowManyS= int(HowManyS*profitSell)
                    continue
                
#############S Owned or Trailing-Stop
            if CurrentRSIS < UpperLimit and len(IntraDayBuys) > 0 and IntraDayBuys[0]==S:
                    
                if CurrentRSIS < LowerLimit:
                    print(ss,"is already owned",nl)
                    pass
                    
                elif CurrentRSIS > LowerLimit:
                    SellPrice=sellProcess(S,ss,HowManyS)
                    if SellPrice > BuyPrice:
                        HowManyT= int(HowManyT*profitSell)
                        HowManyS= int(HowManyS*profitSell)
                    continue
                    
#############  NIBTY    
            if CurrentRSIT > LowerLimit and len(IntraDayBuys) == 0:
                print(tt,"not yet in buying territory")
                pass
#############  NIBTY
            if CurrentRSIS > LowerLimit and len(IntraDayBuys) == 0:
                print(ss,"not yet in buying territory",nl)
                pass
            
############Sell T
            if CurrentRSIT > UpperLimit and len(IntraDayBuys) > 0 and IntraDayBuys[0]==T: 
                SellPrice=sellProcess(T,tt,HowManyT)
                if SellPrice > BuyPrice:
                    HowManyT= int(HowManyT*profitSell)
                    HowManyS= int(HowManyS*profitSell)
                continue
            
############Sell S
            if CurrentRSIS > UpperLimit and len(IntraDayBuys) > 0 and IntraDayBuys[0]==S: 
                SellPrice=sellProcess(S,ss,HowManyS)
                if SellPrice > BuyPrice:
                    HowManyT= int(HowManyT*profitSell)
                    HowManyS= int(HowManyS*profitSell)
                continue
            
        except Exception as e:
            exc+=1
            print(now,"Exception Occurred...")
            print(e,nl)
            e=str(e)
            e=e[0:100]
            if len(IntraDayBuys) > 0:
                message = client.messages \
                                .create(
                                      body="Exception Occurred: "+str(e),
                                      from_='+12564748541',
                                      to=mpn
                                  )
                print(message.sid)
            traceback.print_exc()
            continue

######End of Day Liquidation
    else:
        try:
            if len(IntraDayBuys) > 0:
                t=IntraDayBuys[0]
                if t == T:
                    HowMany=HowManyT
                    which=tt
                    
                elif t == S:
                    HowMany=HowManyS
                    which=ss
                    
                IntraDayBuys.remove(t)
                login()
                sell_order=r.orders.order_sell_market(t, HowMany, timeInForce='gfd', extendedHours=False)
                print("End of Day Liquidation")
                
                while sell_order['state'] != 'filled':
                    login()
                    sell_order=r.orders.get_stock_order_info(sell_order['id'])
                SellPrice=round(float(sell_order['price']),2)

                message = client.messages \
                                .create(
                                      body="EoD Liquidation: Sold "+str(HowMany)+" "+which+" for $"+str(SellPrice),
                                      from_='+12564748541',
                                      to=mpn
                                  )
                print(message.sid)
                time.sleep(120)
                
            while rr < 1:
                totalbuys=0
                exc=0
                rr+=1
                lowestT=100
                lowestS=100
                bought=False
                stopNum=0
                
                HowManyT=howMany(T,overall_percent)
                HowManyS=howMany(S,overall_percent)
                    
                dates=[]
                todays=0
                buys=[]
                sells=[]
                G_L=0
                tickers=[]
                
                returns = pd.read_csv("Trader_Returns.csv", encoding='latin-1',index_col=[0])
                login()
                r.export.export_completed_stock_orders(path, file_name="StockOrders")
                orders = pd.read_csv("StockOrders.csv", encoding='latin-1')
                
                #Deletes partial share buys/sells
                orders=orders[orders.quantity % 1 == 0]
                
                YMD= datetime.now().strftime('%Y-%m-%d')
                    
                #Shorten the dates    
                for i in orders['date']:
                    date=str(i[0:10])
                    dates.append(date)
                orders['date']=dates
                
                #Select only T&S
                orders['ToS']=np.where((orders['symbol'] == T) | (orders['symbol'] == S),True,False)
                orders=orders[orders.ToS  == True]
                    
                #Cut down to todays stuff
                for j in orders['date']:
                    if j == YMD:
                        todays+=1
                orders=orders.head(todays)

                #Cost Basis v Sale Price
                for k in range(0,todays):
                    if orders.iloc[k,3] == 'sell':
                        sells.append(orders.iloc[k,5]*orders.iloc[k,6])
                    elif orders.iloc[k,3] == 'buy':
                        buys.append(orders.iloc[k,5]*orders.iloc[k,6])
                
                G_L= ((sum(sells)-sum(buys))/sum(buys))
                print(round(G_L*100,3),"%")
                
                for l in orders['symbol']:
                    if l not in tickers:
                        tickers.append(l)
                        
                login()
                cash=r.profiles.load_account_profile(info='portfolio_cash')
                print("Cash Balance $",cash,nl)
                HowMuch=float(float(cash)*overall_percent)
                
                new_row={'date':YMD, 'equities':tickers, 'costBasis': sum(buys), 'salePrice':sum(sells), 'perc_change':round(G_L*100,3), 'usd_change':sum(sells)-sum(buys), 'HowMuch':HowMuch}
                returns=returns.append(new_row, ignore_index=True)
                
                returns.to_csv("Trader_Returns.csv")

                message = client.messages \
                                .create(
                                      body="Today's Return: "+str(round(G_L*100,3))+"% or $"+str(round(sum(sells)-sum(buys),2)),
                                      from_='+12564748541',
                                      to=mpn
                                  )
                print(message.sid)
                
        except ZeroDivisionError:
            new_row={'date':YMD, 'equities':"No Trade"}
            returns=returns.append(new_row, ignore_index=True)
            returns.to_csv("Trader_Returns.csv")
            print("No Trades Today")
            message = client.messages \
                            .create(
                                  body="No Trades Today",
                                  from_='+12564748541',
                                  to=mpn
                              )
            print(message.sid)
        
        except Exception as e:
            exc+=1
            print(now,"Exception Occurred... Not During Trading Hours")
            print(e,nl)
            e=str(e)
            e=e[0:100]
            message = client.messages \
                            .create(
                                  body="EoD Exception Occurred: "+str(e),
                                  from_='+12564748541',
                                  to=mpn
                              )
            print(message.sid)
            traceback.print_exc()
            continue
