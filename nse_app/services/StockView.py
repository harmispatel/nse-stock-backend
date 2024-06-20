import requests
import json
from nse_app.Scheduler.helper import Helper
def StockApiCall(name):
    
    baseurl = "https://www.nseindia.com/"
    headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                        'like Gecko) '
                        'Chrome/80.0.3987.149 Safari/537.36',
        'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    session = requests.Session()
    req = session.get(baseurl, headers=headers, timeout=5)
    cookies = dict(req.cookies)
    url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + name

    response = requests.get(url, headers=headers, timeout=5, cookies=cookies)
    data = response.text
    api_data = json.loads(data)
    
    return api_data

def StockviewFun(name):
    
    dict1 = {}
    
    api_data = StockApiCall(name)

    timestamp = api_data['records']['timestamp']
    livePrice = api_data['records']['underlyingValue']
    filteredData = api_data['filtered']['data']

    down_price = Helper.downPrice(filteredData, livePrice)

    up_price = Helper.upPrice(filteredData, livePrice)
    
    downSliceList = Helper.downMaxValue(down_price[:-6:-1])

    upSliceList = Helper.upMaxValue(up_price[0:5])

    PEMax, PEMaxValue = Helper.basePriceData(down_price[:-6:-1], downSliceList)
    
    CEMax, CEMaxValue = Helper.resistancePriceData(up_price[0:5], upSliceList)

    pcr = Helper.pcrValue(api_data)
    
    dict1['name'] = name
    dict1['timestamp'] = timestamp
    dict1['pcr'] = pcr
    dict1['livePrice'] = livePrice
    dict1['PEMax'] = PEMax
    dict1['CEMax'] = CEMax
    dict1['down_price'] = down_price
    dict1['up_price'] = up_price

    
    return dict1