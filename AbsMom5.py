#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
#===========================================================================================================
Copyright 2006-2021 Paseman & Associates (www.paseman.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

#===========================================================================================================
compareYND() calculates monthlyAbsMom5 timing signal using 3 different inputs:
o monthlyAbsMom5Yahoo   - uses SPY and IRX from Yahoo (If panadasbdatareader is down, I use a cached file.)
o monthlyAbsMom5Norgate - uses SPY and IRX from Norgate (Thanks Don for these files)
o monthlyAbsMom5Don     - uses SPY and IRX from other files supplied by Don

compareYND() runs all three, concatenates them and compares the pairwise Buy/Sell Signals  between norgate/yahoo and norgate/don
Note that Norgate/Yahoo gives an error on 2001-05-31 wiith Yahoo raising a spurious(?) sell signal.
The reason is clear.  Yahoo data shows a (slight) monthly decrease in SPY while Norgate/Don show a sight increase.

Note also the following discrepancies for 11/29/2019, the Friday after thanksgiving.
Don's Tbill File
11/29/2019 12:00 AM	13.8485032869658	13.8485032869658	13.8485032869658	13.8485032869658	0	13.8485032869658	13.8485032869658
Yahoo's IRX history - https://finance.yahoo.com/quote/%5EIRX/history?period1=1561852800&period2=1625011200&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true
Nov 29, 2019	-	-	-	-	-	-
Norgates IRX history
20191129	1.553	1.553	1.54	1.54

So either my code samples the data incorrectly, or the data sources do not match.
Feedback appreciated.
"""
import numpy as np
import pandas as pd
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 350)
pd.set_option('display.max_rows', None)

#===========================================================================================================
def monthlyAbsMom5(df,overRideTbillEC=[]): # df has ['%IRX'] and ["SPY"]
  """Calculate monthlyAbsMom5() as per Don Maurer May 2, 2021, 7:47 PM"""
  # For Tbill I calculate an equity curve for it using the t-bill yield ^IRX.
  # Daily return for date i is (1+^IRX(i)/100)^(1/252).
  df['%IRXsmoothed']=(1 + df['%IRX']/100.0)**(1.0/252.0)
  # Then I use those returns to create the TBILL EC.
  # TBILL[0]=10 – an arbitrary starting value for the first date for ^IRX
  df['%IRXsmoothed'].iloc[0]=10
  # TBILL[i] = TBILL[i-1]*(1+^IRX[i-1]/100)^(1/252), for i=1-last ^IRX-1
  df['tbillEC']=df['%IRXsmoothed'].cumprod()
  if len(overRideTbillEC)>0: df['tbillEC']=overRideTbillEC
  #print(df)

  # For absm2M(5,1)(spy,tbill) I use month end prices – not 105 days back.
  # df.fillna(0).resample('BM').last() includes invalid dates like 20020328 (Good Friday), 20040528, 20100528
  # Instead of calendars, depend on the fact that SPY and IRX are only quoted on dates that market is open.
  # https://stackoverflow.com/questions/48288059/how-to-get-last-day-of-each-month-in-pandas-dataframe-index-using-timegrouper
  Mdf=df.loc[df.groupby(df.index.to_period('M')).apply(lambda x: x.index.max())]


  # Then I compute absmM(5)(spy,tbill) = gainM5(Spy) – gainM5(Tbill)
  # and similarly for absmM(1)(spy,tbill)=gainM1(spy)-gainM1(tbill).
  Mdf['absmM(5)']=Mdf["SPY"].pct_change(periods=5)-Mdf["tbillEC"].pct_change(periods=5)
  Mdf['absmM(1)']=Mdf["SPY"].pct_change(periods=1)-Mdf["tbillEC"].pct_change(periods=1)
  # If either absmM(5)(spy,tbill) or absmM(1)(spy,tbill) is >=0, you are in equities.
  # You need both negative to be in cash.
  Mdf['SELL']=np.where(((Mdf['absmM(5)']<0.0) & (Mdf['absmM(1)']<0.0)), 'SELL','')
  return Mdf['19991231':] # 19940331

#===========================================================================================================
def monthlyAbsMom5Norgate():
  SPY = pd.read_csv("SPY-NorgateExtended.txt",  header=0, sep='\t', index_col=0, parse_dates=True)#.fillna(0)
  IRX = pd.read_csv("^IRX.txt",  header=0, sep='\t', index_col=0, parse_dates=True)#.fillna(0)
  IRX.rename(columns={"Close":'%IRX'}, inplace=True)
  df=pd.concat([SPY["Close"],IRX['%IRX']], axis=1)
  df.rename(columns={"Close":"SPY"}, inplace=True)
  return monthlyAbsMom5(df)

#===========================================================================================================
import pandas_datareader as pdr
import datetime
def getTickerPriceColumnYahoo(ticker,columnName="Close"):
  try:
    start = datetime.datetime(1993, 1, 1)
    end = datetime.datetime(2021, 7, 2)
    df= pdr.get_data_yahoo(ticker, start, end)
  except Exception as ex:
    # https://365datascience.com/question/remotedataerror-unable-to-read-url-for-yahoo-using-pandas-datareader/
    # as of 7/8/2021, get "Our engineers are working quickly to resolve the issue."
    # So retrieve a cached version
    print(ex.args)
    df = pd.read_csv(ticker+".csv",  header=0, index_col=0, parse_dates=True)
  df.rename(columns={columnName:ticker}, inplace=True)
  return df[ticker]
#===========================================================================================================
def monthlyAbsMom5Yahoo():
  df=getTickerPriceColumnYahoo("SPY",columnName="Adj Close").to_frame()
  df["%IRX"]=getTickerPriceColumnYahoo("^IRX")
  return monthlyAbsMom5(df)

#===========================================================================================================
def monthlyAbsMom5Don():
  df=pd.read_csv("SPY-NorgateExtended.txt",header=0, sep='\t', index_col=0, parse_dates=True)['Close'].to_frame()
  df.rename(columns={'Close':'SPY'}, inplace=True)
  df["%IRX"]=pd.read_csv("TBILL.txt",header=0, sep='\t', index_col=0, parse_dates=True)['Close']
  return monthlyAbsMom5(df,df["%IRX"])
#===========================================================================================================
def compareYND():
  dfN=monthlyAbsMom5Norgate()
  dfN.rename(columns={old:"n"+old for old in dfN.columns}, inplace=True)
  dfY=monthlyAbsMom5Yahoo()
  dfY.rename(columns={old:"y"+old for old in dfY.columns}, inplace=True)
  dfD=monthlyAbsMom5Don()
  dfD.rename(columns={old:"d"+old for old in dfD.columns}, inplace=True)
  df=pd.concat([dfN, dfY, dfD], axis=1)
  df['nysellERR'] =np.where(df["nSELL"] == df['ySELL'], '','ERROR')
  df['ndsellERR'] =np.where(df["nSELL"] == df['dSELL'], '','ERROR')
  return df
#===========================================================================================================
if __name__ == '__main__':
  df=compareYND()
  df.to_csv("compareYND.csv")
  print(df)
