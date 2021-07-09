# AbsMom5
#=======================================================================================

Copyright 2006-2021 Paseman & Associates (www.paseman.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

#=======================================================================================

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
