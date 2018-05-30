import requests
import re
from datetime import datetime
import matplotlib.pyplot as plt

base_url = "https://api.binance.com"
klines_query_api = "/api/v1/klines"

def process_kline_data(contents):
    contents = contents.decode('utf-8')
    data = re.split('\[*\]\,', contents)
    ret = {}
    ret['open_time'] = []
    ret['open_datetime'] = []
    ret['open'] = []
    ret['high'] = []
    ret['low'] = []
    ret['close'] = []
    ret['close_time'] = []
    for d in data:
        tmp = d.replace('[', '')
        tmp = tmp.replace('\"', '')
        tmp = tmp.split(',')
        ret['open_time'].append(int(tmp[0]))
        ret['open_datetime'].append(datetime.fromtimestamp(int(tmp[0])/1000))
        ret['open'].append(float(tmp[1]))
        ret['high'].append(float(tmp[2]))
        ret['low'].append(float(tmp[3]))
        ret['close'].append(float(tmp[4]))
        ret['close_time'].append(int(tmp[6]))

    return ret

"""
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore
  ]
]
"""

def get_klines(symbol, interval, startTime=None, endTime=None):
    params = {}
    params['symbol'] = symbol
    params['interval'] = interval

    if startTime:
        params['startTime']=startTime
    if endTime:
        params['endTime'] = endTime

    response = requests.get(base_url+klines_query_api, params)

    if response.status_code == 200:
        return process_kline_data(response.content)

    else:
        raise Exception("Data collection failed. Failed code : " + str(response.status_code))

def main():
    symbol = "BTCUSDT"
    interval = "6h"
    startTime = 1509940000000
    endTime = 1579040000000
    data = get_klines(symbol, interval, startTime)
    print (len(data['open_time']))
    plt.plot(data['open_datetime'], data['open'], label=symbol)
    plt.ylabel(symbol+"($)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()
    return None

if __name__=="__main__":
    main()
