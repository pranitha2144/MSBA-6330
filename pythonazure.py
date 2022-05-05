# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 18:35:10 2022

@author: prani
"""
import os
import pandas as pd
import json
from yahoo_fin import stock_info as si
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from azure.eventhub.exceptions import EventHubError
import asyncio

import pandas as pd
import requests
from yahoo_fin import stock_info as si
import nltk
#nltk.download('stopwords')
from nltk.corpus import stopwords
import numpy as np

#from datetime import datetime
#the above is used to convert some columns in the dataframe- not needed in demo

connection_str=os.getenv('Azure_ConnectionString')
eventhub_name=os.getenv('Azure_EventHub')


def getWSBStocks():

    # Setting up Reddit API
    # Source: https://towardsdatascience.com/how-to-use-the-reddit-api-in-python-5e05ddfd1e5c
    client_id = os.getenv('client_id')
    secret_key = os.getenv('secret_key')
    
    auth = requests.auth.HTTPBasicAuth(client_id, secret_key)
    
    data = {'grant_type':'password',
            'username': os.getenv('username'),
            'password': os.getenv('password')}
    
    headers = {'User-Agent': 'MyApi/0.0.1'}
    
    res = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
    
    token = res.json()['access_token']
    
    headers = {**headers, **{'Authorization': f"bearer {token}"}}
    
    # make a request for the trending posts in /r/WSB
    res = requests.get("https://oauth.reddit.com/r/wallstreetbets/hot",
                       headers=headers, params={'limit':100})
    
    # Data frame to fill with stock data
    df = pd.DataFrame()
    
    # loop through each post retrieved from GET request
    for post in res.json()['data']['children']:
        # append relevant data to dataframe
        df = df.append({
            'title': post['data']['title'],
            'selftext': post['data']['selftext'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score']
        }, ignore_index=True)
        
    # Source: https://levelup.gitconnected.com/how-to-get-all-stock-symbols-a73925c16a1b 
    # Get stock tickers from Yahoo Finance
    df1 = pd.DataFrame( si.tickers_sp500() )
    df2 = pd.DataFrame( si.tickers_nasdaq() )
    df3 = pd.DataFrame( si.tickers_dow() )
    df4 = pd.DataFrame( si.tickers_other() )
    
    sym1 = set( symbol for symbol in df1[0].values.tolist() )
    sym2 = set( symbol for symbol in df2[0].values.tolist() )
    sym3 = set( symbol for symbol in df3[0].values.tolist() )
    sym4 = set( symbol for symbol in df4[0].values.tolist() )
    
    symbols = set.union( sym1, sym2, sym3, sym4 )
    
    # list to remove delinquent stocks
    my_list = ['W', 'R', 'P', 'Q']
    
    del_set = set()
    sav_set = set()
    
    # removing delinquent stocks
    for symbol in symbols:
        if len( symbol ) > 4 and symbol[-1] in my_list:
            del_set.add( symbol )
        else:
            sav_set.add( symbol )
    
    # grab the relevent stocks from the titles
    stocks = []
    for item in df['title']:
      for i in item.split():
        if i in sav_set:
          stocks.append(i)
    
    
    # Remove stop words from stock list
    filtered_stocks = []
    for item in stocks:
        if item.lower() not in stopwords.words('english'):
            filtered_stocks.append(item)
    
    # Removing common non Stock Ticker words
    common_words = ['YOLO', 'MEME', 'IRS', 'HUGE', 'LOVE']
    
    for word in common_words:
        if word in filtered_stocks:
            filtered_stocks.remove(word)
    t=np.unique(np.array(filtered_stocks))
    top10=[]
    for i in range(len(t)):
        if(i<10):
            top10.append(t[i])
    return top10
def getstockdata():
    df1=pd.DataFrame()
    #getting trending stocks using the function created above
    df1["Symbol"]=getWSBStocks()
    names=[]
    for i in df1["Symbol"]:
        names.append(si.get_quote_data(i)["shortName"])
    df1["Name"]=names

    #live price of stock
    df1["livePrice"]=df1["Symbol"].apply(si.get_live_price)
    
    #PE ratio
    #peratio=[]
    #for i in df1["Symbol"]:
        #peratio.append(si.get_quote_table(i)["PE Ratio (TTM)"])
    #df1["PE Ratio (TTM)"]=peratio
    
    #stock volume in millions
    #PE ratio
    stkvol=[]
    for i in df1["Symbol"]:
        stkvol.append(si.get_quote_table(i)["Volume"]/1000000)
    df1["Volume_inMill"]=stkvol
    
    
    #50daymovavg
    movavgs=[]
    for i in df1["Symbol"]:
        movavgs.append(si.get_data(i, interval='1d')['close'][-50:].mean())
        
    df1["fiftydaymovavg"]=movavgs
    
    
    
    #200daymovavg
    movavgs=[]
    for i in df1["Symbol"]:
        movavgs.append(si.get_data(i, interval='1d')['close'][-200:].mean())
    df1["twohundaymovavg"]=movavgs

    #previous day closing price
    import yfinance as yf
    yestprices=[]
    for i in df1["Symbol"]:
        yestprices.append(yf.download( tickers = i,period = "2d",interval = "1d").iloc[0,3])
    df1["prevdayclosingprice"]=yestprices

    #1 month price history
    df2=pd.DataFrame()
    monthlypricehistory=[]
    symbols=[]
    symbolindex=[]
    dates=[]
    for t in range(len(df1["Symbol"])):
        i=df1["Symbol"][t]
        monthlypricehistory.extend(list(yf.download( tickers = i,period = "1mo",interval = "1d")["Close"].values))
        dates.extend(list(yf.download( tickers = i,period = "1mo",interval = "1d").index.astype(str)))
        symbolindex.extend([t for i in  range(len(list(yf.download( tickers = i,period = "1mo",interval = "1d")["Close"].values)))])
        symbols.extend([i for k in  range(len(list(yf.download( tickers = i,period = "1mo",interval = "1d")["Close"].values)))])
    df2["Symbol"]=pd.Series(symbols)
    df2["Symbolindex"]=pd.Series(symbolindex)
    df2["DailyPrice"]=pd.Series(monthlypricehistory)
    df2["Date"]=pd.Series(dates)
    df1=pd.merge(df1,df2, on="Symbol")
    df1.index.name='Index'
    return df1.to_dict("record")


#defining a function that updates data real time(at defined frequency)
async def run():
    while True:
        
        producer = EventHubProducerClient.from_connection_string(conn_str=connection_str, eventhub_name=eventhub_name)
        async with producer:
            # Create a batch.
            event_data_batch = await producer.create_batch()
            
            # Add events to the batch.
            event_data_batch.add(EventData(json.dumps(getstockdata())))
            
            # Send the batch of events to the event hub.
            await producer.send_batch(event_data_batch)
            print("success")
    await asyncio.sleep(30)#run this every 1/2 mins
        
dataloop=asyncio.get_event_loop()
try:
    asyncio.ensure_future(run())
    dataloop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("closing loop now")
    dataloop.close()