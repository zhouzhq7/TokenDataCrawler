import requests
import re
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt

base_url = "https://api.binance.com"
klines_query_api = "/api/v1/klines"
price_query_api = "/api/v3/ticker/price"
default_save_dir = "save"

KLINE_INTERVAL_1MINUTE = '1m'
KLINE_INTERVAL_3MINUTE = '3m'
KLINE_INTERVAL_5MINUTE = '5m'
KLINE_INTERVAL_15MINUTE = '15m'
KLINE_INTERVAL_30MINUTE = '30m'
KLINE_INTERVAL_1HOUR = '1h'
KLINE_INTERVAL_2HOUR = '2h'
KLINE_INTERVAL_4HOUR = '4h'
KLINE_INTERVAL_6HOUR = '6h'
KLINE_INTERVAL_8HOUR = '8h'
KLINE_INTERVAL_12HOUR = '12h'
KLINE_INTERVAL_1DAY = '1d'
KLINE_INTERVAL_3DAY = '3d'
KLINE_INTERVAL_1WEEK = '1w'
KLINE_INTERVAL_1MONTH = '1M'

def get_prices():
    response = requests.get(base_url + price_query_api)

    if response.status_code == 200:
        data = response.content
        data = data.decode('utf-8')
        return data

    else:
        raise Exception("Data collection failed. Failed code : " + str(response.status_code))

def process_kline_data(contents):
    contents = contents.decode('utf-8')
    data = re.split('\[*\]\,', contents)
    ret = []
    for d in data:
        tmp = d.replace('[', '')
        tmp = tmp.replace(']', '')
        tmp = tmp.replace('\"', '')
        tmp = tmp.split(',')
        #tmp = [str(datetime.fromtimestamp(int(tmp[0])/1000))] + tmp
        ret.append(tmp)

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

def save_data_to_csv(symbol, interval, data):
    save_dir = os.path.join(default_save_dir, symbol)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    csv_file_name = symbol+'_'+interval+".csv"
    csv_file_path = os.path.join(save_dir, csv_file_name)

    with open(csv_file_path, 'a') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def csv_file_write_headers(symbol, interval):
    save_dir = os.path.join(default_save_dir, symbol)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    csv_file_name = symbol + '_' + interval + ".csv"
    csv_file_path = os.path.join(save_dir, csv_file_name)

    if os.path.isfile(csv_file_path):
        os.remove(csv_file_path)
    header = [['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
              'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
              'Taker buy quote asset volume', 'Ignore']]
    with open(csv_file_path, 'a') as f:
        writer = csv.writer(f)
        writer.writerows(header)

def interval_to_millisecond(interval):
    if interval == KLINE_INTERVAL_1MINUTE:
        return 60000
    elif interval == KLINE_INTERVAL_15MINUTE:
        return 15*60*1000
    elif interval == KLINE_INTERVAL_2HOUR:
        return 2*60*60*1000
    else:
        raise Exception(interval + " is not supported in current version")

def main():

    symbol = "BTCUSDT"
    interval = "1m"

    startTime = 1495000000000
    csv_file_write_headers(symbol, interval)
    while True:
        print ("Collecting data on date : " + str(datetime.fromtimestamp(startTime/1000)))
        data = get_klines(symbol, interval, startTime)
        startTime = int(data[-1][0]) + interval_to_millisecond(interval)
        save_data_to_csv(symbol,interval, data)
        if len(data) < 1000:
            print ("The last data collected is on date : " + str(datetime.fromtimestamp(int(data[-1][0])/1000)))
            break



    return None

if __name__=="__main__":
    main()
