from nse_app.models import *
from django.utils import timezone
import datetime
from datetime import date, datetime as dt
import requests
import json
from datetime import timedelta
from rich.console import Console
from .helper import Helper
from .sell_function import sellFunOption, futureLivePrice, optionFuture, ltpData
import os
from dotenv import load_dotenv
from .utils import cPrint, cLogs, currentDateTime, formatTime, get_daily_log_file, oiDiff, formatDate, nearest_previous_15_min_from_list, getSpotPriceFromDB
from nse_app.utils import api_headers
load_dotenv()

consoleGreen = Console(style='green')
consoleRed = Console(style='red')


# VARIABLES LOCAL AND SERVER BOTH ARE SAME
BANKNIFTY_CE = os.getenv('BANKNIFTY_CE')
BANKNIFTY_PE = os.getenv('BANKNIFTY_PE')
BANKNIFTY_FUTURE = os.getenv('BANKNIFTY_FUTURE')

BANKNIFTY_URL = os.getenv('BANKNIFTY_URL')
SETTINGS_URL = os.getenv('SETTINGS_URL')
# SETTINGS_URL = 'http://zerodha.harmistechnology.com/settings'

def bankniftyApiFun():
    ##  Set variable as global to use across different functions 
    global api_data, livePrice, timestamp, filteredData, PEMax, CEMax, down_price, up_price, downSliceList, upSliceList, pcr, base_Price_down, base_Price_up
    global up_first_total_oi, down_first_total_oi, CEMaxValue, PEMaxValue, exprityDate, oi_total_call, oi_total_put

    url = BANKNIFTY_URL
    file = open(get_daily_log_file('banknifty'), "a")
    try:
        api_data = requests.get(url, headers=api_headers).json()
    except Exception as e:
        consoleRed.print(f'{currentDateTime()} ::: BANKNIFTY -----> ERROR in nse banknifty API -> {str(e)}')
        cLogs(file, f'-------> ERROR in nse banknifty API -> {str(e)}', False)

    
    timestamp = api_data['records']['timestamp']
    livePrice = api_data['records']['underlyingValue']
    filteredData = api_data['filtered']['data']
    
    date_string = api_data['records']['expiryDates'][0]
    date_format = "%d-%b-%Y"
    date_object = dt.strptime(date_string, date_format).date()
    exprityDate = date(date_object.year, date_object.month, date_object.day)
    
    ## Check coustom conditions to get data from optionchain 
    down_price = Helper.downPrice(filteredData, livePrice)
    up_price = Helper.upPrice(filteredData, livePrice)
    
    downSliceList = Helper.downMaxValue(down_price[:-6:-1])
    upSliceList = Helper.upMaxValue(up_price[0:5])
    
    PEMax, PEMaxValue = Helper.basePriceData(down_price[:-6:-1], downSliceList)
    CEMax, CEMaxValue = Helper.resistancePriceData(up_price[0:5], upSliceList)
    
    pcr = Helper.pcrValue(api_data)
    pcr = round(pcr, 2)
    
    down_first_total_oi = ((down_price[-1]['PE']['changeinOpenInterest'] + down_price[-1]['PE']['openInterest']) - (down_price[-1]['CE']['changeinOpenInterest'] + down_price[-1]['CE']['openInterest']))
    up_first_total_oi = ((up_price[0]['PE']['changeinOpenInterest'] + up_price[0]['PE']['openInterest']) - (up_price[0]['CE']['changeinOpenInterest'] + up_price[0]['CE']['openInterest']))
    
    '''find call strike price for buy'''
    base_Price_down = []
    Total_oi_down_arr = []
    for downSlice3 in down_price[:-5:-1]:
        PE_oi_down = downSlice3['PE']['changeinOpenInterest'] + downSlice3['PE']['openInterest']
        CE_oi_down = downSlice3['CE']['changeinOpenInterest'] + downSlice3['CE']['openInterest']
        Total_oi_down = PE_oi_down - CE_oi_down
        Total_oi_down_arr.append(Total_oi_down)
        if Total_oi_down > oi_total_call:
            if abs(Total_oi_down_arr[0]) == abs(Total_oi_down):
                if up_first_total_oi < abs(Total_oi_down_arr[0]):
                    base_Price_down.append(downSlice3)
                    break
                else:
                    continue
            base_Price_down.append(downSlice3)
            break
    
    '''find put strike price for buy'''
    base_Price_up = []
    Total_oi_up_arr = []
    for upSlice3 in up_price[0:5]:
        PE_oi_up = upSlice3['PE']['changeinOpenInterest'] + upSlice3['PE']['openInterest']
        CE_oi_up = upSlice3['CE']['changeinOpenInterest'] + upSlice3['CE']['openInterest']
        Total_oi_up = PE_oi_up - CE_oi_up
        Total_oi_up_arr.append(Total_oi_up)
        if abs(Total_oi_up) > oi_total_put and Total_oi_up < 0 :
            if abs(Total_oi_up_arr[0]) == abs(Total_oi_up):
                if down_first_total_oi < abs(Total_oi_up_arr[0]):
                    base_Price_up.append(upSlice3)  
                    break 
                else:
                    continue
            base_Price_up.append(upSlice3)  
            break 

def settingFun():
    
    global stock_details, nseSetting, live_obj, pcr_options, is_live_banknifty, is_op_fut_banknifty
    global PcrObj_Call_ID, banknifty_pcr_stoploss_CALL, banknifty_at_set_pcr_CALL, banknifty_live_pcr, PcrObj_Put_ID, banknifty_pcr_stoploss_PUT, banknifty_at_set_pcr_PUT
    global set_CALL_pcr, basePlus_CALL, profitPercentage_CALL, lossPercentage_CALL, lot_size_CALL
    global set_PUT_pcr, basePlus_PUT, profitPercentage_PUT, lossPercentage_PUT, lot_size_PUT
    global used_logic_put, used_logic_call, oi_total_put, oi_total_call, profitFuture, lossFuture, lotSizeFuture
    global OptionId_CALL, OptionId_PUT, OptionId_Future
    global setBuyCondition_CALL, setOneStock_CALL, setBuyCondition_PUT, setOneStock_PUT, setBuyConditionFutureBuy, setBuyConditionFutureSell
    file = open(get_daily_log_file('banknifty'), "a")

    ## LOCAL SETTINGS 
    stock_details = stock_detail.objects.values().order_by("-buy_time")[:50]
    nseSetting = nse_setting.objects.values()
    live_obj = live.objects.values()
    pcr_options = pcr_option.objects.values()
    
    for pcrobj in pcr_options:
        if pcrobj['OptionName'] == 'BankNiftyPcrCALL':
            PcrObj_Call_ID = pcrobj['id']
            banknifty_pcr_stoploss_CALL = pcrobj['PcrStopLoss']
            banknifty_at_set_pcr_CALL = pcrobj['AtSetPcr']
            banknifty_live_pcr = pcrobj['LivePcr']
        if pcrobj['OptionName'] == 'BankNiftyPcrPUT':
            PcrObj_Put_ID = pcrobj['id']
            banknifty_pcr_stoploss_PUT = pcrobj['PcrStopLoss']
            banknifty_at_set_pcr_PUT = pcrobj['AtSetPcr']
            banknifty_live_pcr = pcrobj['LivePcr']

    ## API SETTINGS ZERODHA HARMIS
    settings_url = SETTINGS_URL
    try:
        settings_data = requests.get(settings_url).json()
    except Exception as e:
        consoleRed.print(f'{currentDateTime()} ::: BANKNIFTY -------> ERROR in settings API -> {str(e)}')
        cLogs(file, f'-------> ERROR in settings API -> {str(e)}')

    settings_data_api = settings_data['data']
    is_live_banknifty = settings_data['liveSettings'][0]['live_banknifty']
    is_op_fut_banknifty = settings_data['liveSettings'][0]['op_fut_banknifty']

    for k in settings_data_api:
        if k['option'] == BANKNIFTY_CE:       ## Name as per server DB
            set_CALL_pcr = k['set_pcr']
            basePlus_CALL = k['baseprice_plus']
            profitPercentage_CALL = k['profit_percentage']
            lossPercentage_CALL = k['loss_percentage']
            lot_size_CALL = k['quantity_bn']
            used_logic_call = k['used_logic']
            oi_total_call = k['oi_total']
            
        if k['option'] == BANKNIFTY_PE:       ## Name as per server DB
            set_PUT_pcr = k['set_pcr']
            basePlus_PUT = k['baseprice_plus']
            profitPercentage_PUT = k['profit_percentage']
            lossPercentage_PUT = k['loss_percentage']
            lot_size_PUT = k['quantity_bn'] 
            used_logic_put = k['used_logic']
            oi_total_put = k['oi_total']

        if k['option'] == BANKNIFTY_FUTURE:
            profitFuture = k['profit_percentage']
            lossFuture = k['loss_percentage']
            lotSizeFuture = k['quantity_bn'] 

    ## find ID of order in local database 
    for k in nseSetting:
        if k['option'] == BANKNIFTY_CE:       ## Name as per Local DB
            OptionId_CALL = k['id']
        if k['option'] == BANKNIFTY_PE:       ## Name as per Local DB
            OptionId_PUT = k['id']      
        if k['option'] == BANKNIFTY_FUTURE:       ## Name as per Local DB
            OptionId_Future = k['id']        
    
    ## Check order table is exit, if not then set some field as null in variable
    if stock_details.exists():
        pass
    else:
        now = datetime.datetime.now()
        yesterday = now - timedelta(days = 1)
        stock_details = [{'percentage_id':0, "status": '', "call_put":"", 'buy_time':yesterday }]


    ## CALL Buy Condition
    setBuyCondition_CALL, setOneStock_CALL = Helper.buyCondition_withOneStock(stock_details, OptionId_CALL, "CALL", "BANKNIFTY")
    ## PUT Buy Condition
    setBuyCondition_PUT, setOneStock_PUT = Helper.buyCondition_withOneStock(stock_details, OptionId_PUT, "PUT", "BANKNIFTY")
    ## FUTURE BUY Condition
    setBuyConditionFutureBuy = Helper.buyConditionFuture(stock_details, OptionId_Future, 'BUY')
    ## FUTURE SELL Condition
    setBuyConditionFutureSell = Helper.buyConditionFuture(stock_details, OptionId_Future, 'SELL')


def BANKNIFTY():
    ''' Set time to run function in given time '''
    global today, current_time
    current_time = datetime.datetime.now().time()
    today = datetime.datetime.today()
    start_time = datetime.time(hour=9, minute=15)
    end_time = datetime.time(hour=15, minute=15)
    
    if start_time <= current_time <= end_time:
        try:
            '''
            Call both function, It sets variable in global, we can use them here 
            '''
            settingFun()
            bankniftyApiFun()

            ## Condition functions
            buyOnOptionGivenTime()
            # callBuy()                 
            # putBuy()
            # futureBuy()
            # futureSell()
            # futureExitStock()
        
            
            ## CALL SELL                    
            sell_stock_logic(stock_details, OptionId_CALL, filteredData, pcr)
            ## PUT SELL
            sell_stock_logic(stock_details, OptionId_PUT, filteredData, pcr)
        
        except Exception as e:
            pass
            # consoleRed.print('Error in BANKNIFTY ------>', e)
            # consoleRed.print("There is some Internal error ............................................. BANKNIFTY")


def buyOnOptionGivenTime():
    ''' 
        Automactically buy on specific time
        Strike price: first In the money
    '''
    url = 'https://nseindia.harmistechnology.com/api/currentDateGrah'
    isBuyCondition = Helper.isBuyCondition(stock_details, OptionId_CALL)

    file = open(get_daily_log_file('banknifty'), "a")
    if isBuyCondition == True:
        try:
            response = requests.post(url, {
                "date": formatDate(today)
                # 'date': '2024-07-12'
            }).json()
        except Exception as e:
            consoleRed.print(f'{currentDateTime()} ::: BANKNIFTY -------> ERROR - currentDateGrah API failed -> {str(e)}')        
            cLogs(file, f'-------> ERROR - currentDateGrah API failed -> {str(e)}')

        if response['success'] == True:
            for data in response['data']['data']:
                # data = response['data']['data'][0]
                end_time = formatTime(data['end_time'])
                cLogs(file, f'BANKNIFTY --> end_time: {end_time} - current_time: {formatTime(current_time)} ')

                if end_time == formatTime(current_time) and data['featureby_or_optionby'] == 'Option' and (data['nifty_or_banknifty'] == 'BANKNIFTY' or data['nifty_or_banknifty'] == 'Both'):
                    cLogs(file, f'=============> BUYING ON {today.date()} at {end_time} ')  
                    if  data['buy_or_sale'] != 'BUY' or 'SELL': 
                        nearest_previous_15_min = nearest_previous_15_min_from_list(formatTime(current_time))
                        if nearest_previous_15_min != None:
                            record_given_time, record_15_min_before = getSpotPriceFromDB(nearest_previous_15_min, 'BANKNIFTY', pcr_values)
                            if record_given_time is not None and record_15_min_before is not None:
                                if record_given_time.live_price > record_15_min_before.live_price:
                                    data['buy_or_sale'] = 'SELL'
                                else:
                                    data['buy_or_sale'] = 'BUY'

                    if data['buy_or_sale'] != 'BUY' and data['buy_or_sale'] != 'SELL':
                        buy_or_sale = data['buy_or_sale']
                        cLogs(file, f'BANKNIFTY - CAN NOT FIND buy_or_sale status to place order -> buy_or_sale: {buy_or_sale}, record_given_time: {str(record_given_time)}, record_15_min_before: {str(record_15_min_before)}')

                    bidPrice = 0
                    if data['buy_or_sale'] == 'BUY':
                        call_or_put = 'CALL'
                        OptionId = OptionId_CALL
                        strikeData = down_price[-1]
                        strikePrice = strikeData['strikePrice']
                        bidPrice = ltpData('BANKNIFTY', strikePrice, 'CE', exprityDate)
                        targetPrice = bidPrice + int(data['target_price'])
                        stopLossPrice = bidPrice - (int(data['target_price']) / 2)
                        cLogs(file, f'{call_or_put} BUY -> strikePrice: {strikePrice}, bidPrice: {bidPrice} ')
                    if data['buy_or_sale'] == 'SELL':
                        call_or_put = 'PUT'
                        OptionId = OptionId_PUT
                        strikeData = up_price[0]
                        strikePrice = strikeData['strikePrice']
                        bidPrice = ltpData('BANKNIFTY', strikePrice, 'PE', exprityDate)
                        targetPrice = bidPrice + int(data['target_price'])
                        stopLossPrice = bidPrice - (int(data['target_price']) / 2)
                        cLogs(file, f'{call_or_put} BUY -> strikePrice: {strikePrice}, bidPrice: {bidPrice} ')

                    if bidPrice:
                        sell_data = stock_detail.objects.create(
                            status="BUY", 
                            qty= int(data['quantity'])*15, 
                            buy_price = bidPrice, 
                            base_strike_price=strikePrice, 
                            live_Strike_price=livePrice, 
                            live_brid_price=bidPrice, 
                            sell_price= targetPrice ,
                            stop_loseprice=stopLossPrice, 
                            percentage_id=OptionId , 
                            call_put =call_or_put, 
                            buy_pcr = '%.2f'% (pcr) 
                        )
                        cLogs(file, f'BANKNIFTY Trade is placed in db at price {bidPrice} on {today.date()} {formatTime(current_time)} ')

                        if is_live_banknifty == True:
                            try:
                                sellFunOption(strikePrice, bidPrice, data['target_price'], str(int(data['target_price']) / 2), OptionId, int(data['quantity']), sell_data.id, exprityDate)    
                                cLogs(file, f'BANKNIFTY SUCCESSFULLY BUY in live broker {bidPrice} on {today.date()} {formatTime(current_time)} ')
                            except Exception as e:
                                cLogs(file, f'BANKNIFTY ERROR =======> GETTING ERROR WHILE PLACING TRADE IN LIVE BROKER -> {str(e)} ')
                        break
                    else:
                        cLogs(file, f'BANKNIFTY Something wrong with bidPrice and other data ')
        else:
            consoleRed.print(f'{currentDateTime()} ::: ERROR - somthing wrong with"currentDateGrah" API')
            cLogs(file, f'BANKNIFTY ERROR - somthing wrong with "currentDateGrah" API ', False)

def callBuy():
    if is_op_fut_banknifty == 'OPTION' and setOneStock_CALL == True and setBuyCondition_CALL == True and pcr >= set_CALL_pcr:
        for nbpd in base_Price_down:
            call_call = "CALL"
            basePricePlus_CALL = nbpd['strikePrice'] + basePlus_CALL
            basePricePlus_CALL_a = basePricePlus_CALL - 15
            print(f'-------------------------------------------------------------------> BANKNIFTY CE: {basePricePlus_CALL_a} < {livePrice} < {basePricePlus_CALL}')
            if basePricePlus_CALL_a <= livePrice and livePrice <= basePricePlus_CALL:
                BidPrice_CE = nbpd['CE']['bidprice']
                strikePrice_CE = nbpd['strikePrice']
                squareoff_CE = '%.2f'% (( BidPrice_CE * profitPercentage_CALL ) / 100)
                stoploss_CE = '%.2f'% ((BidPrice_CE * lossPercentage_CALL ) / 100)
                sellPrice_CE = '%.2f'% ((BidPrice_CE * profitPercentage_CALL) / 100 + BidPrice_CE)
                stop_loss_CE = '%.2f'% (BidPrice_CE - (BidPrice_CE * lossPercentage_CALL ) / 100)
                
                postData = { "buy_price": BidPrice_CE, "base_strike_price":strikePrice_CE, "live_Strike_price":livePrice, "sell_price": sellPrice_CE, "stop_loseprice": stop_loss_CE, 'percentage': OptionId_CALL, 'call_put':call_call}
                obj_banknifty_old = stock_detail.objects.create(
                    status="BUY", 
                    qty= lot_size_CALL*15, 
                    buy_price = BidPrice_CE, 
                    base_strike_price=strikePrice_CE, 
                    live_Strike_price=livePrice, 
                    live_brid_price=BidPrice_CE, 
                    sell_price= sellPrice_CE ,
                    stop_loseprice=stop_loss_CE, 
                    percentage_id=OptionId_CALL , 
                    call_put =call_call, 
                    buy_pcr = '%.2f'% (pcr) 
                )
                if is_live_banknifty == True:
                    sellFunOption(strikePrice_CE, BidPrice_CE, squareoff_CE, stoploss_CE, OptionId_CALL, lot_size_CALL, obj_banknifty_old.id, exprityDate)
                print(f'SuccessFully Buy IN BANKNIFTY CALL: {postData}') 


def putBuy():
    ## PUT BUY
    if is_op_fut_banknifty == 'OPTION' and setOneStock_PUT == True and setBuyCondition_PUT == True and pcr <= set_PUT_pcr:
        for bpu in base_Price_up:
            put_put = "PUT"
            basePricePlus_PUT = bpu['strikePrice'] + basePlus_PUT
            basePricePlus_PUT_a = basePricePlus_PUT + 15
            print(f'-------------------------------------------------------------------> BANKNIFTY PE: {basePricePlus_PUT} < {livePrice}, < {basePricePlus_PUT_a}')
            if basePricePlus_PUT <= livePrice and livePrice <= basePricePlus_PUT_a:
                BidPrice_PUT = bpu['PE']['bidprice']
                strikePrice_PUT = bpu['strikePrice']
                squareoff_PUT = '%.2f'% (( BidPrice_PUT * profitPercentage_PUT ) / 100)
                stoploss_PUT = '%.2f'% ((BidPrice_PUT * lossPercentage_PUT ) / 100)
                sellPrice_PUT = '%.2f'% ((BidPrice_PUT * profitPercentage_PUT) / 100 + BidPrice_PUT)
                stop_loss_PUT = '%.2f'% (BidPrice_PUT - (BidPrice_PUT * lossPercentage_PUT ) / 100)
                postData = { "buy_price": BidPrice_PUT, "base_strike_price":strikePrice_PUT, "live_Strike_price":livePrice, "sell_price": sellPrice_PUT, "stop_loseprice": stop_loss_PUT, 'percentage': OptionId_PUT, 'call_put':put_put}
                
                obj_banknifty_old = stock_detail.objects.create(
                    status="BUY", 
                    qty= lot_size_PUT*15, 
                    buy_price = BidPrice_PUT,
                    live_brid_price=BidPrice_PUT , 
                    base_strike_price=strikePrice_PUT, 
                    live_Strike_price=livePrice, 
                    sell_price= sellPrice_PUT ,
                    stop_loseprice=stop_loss_PUT, 
                    percentage_id=OptionId_PUT , 
                    call_put =put_put, 
                    buy_pcr = '%.2f'% (pcr) 
                    )
                if is_live_banknifty == True:
                    sellFunOption(strikePrice_PUT, BidPrice_PUT, squareoff_PUT, stoploss_PUT, OptionId_PUT, lot_size_PUT, obj_banknifty_old.id, exprityDate)
                print(f'SuccessFully Buy IN BANKNIFTY PUT: {postData}')


def futureBuy():
    ## FUTURE BUY
    if is_op_fut_banknifty == 'FUTURE' and setBuyConditionFutureBuy == True and pcr >= set_CALL_pcr:
        for nbpd in base_Price_down:
            basePricePlus_FUT = nbpd['strikePrice'] + basePlus_CALL
            basePricePlus_FUT_a = basePricePlus_FUT - 15
            print(f'-------------------------------------------------------------------> BANKNIFTY FUTURE BUY: {basePricePlus_FUT_a} < {livePrice} <  {basePricePlus_FUT}')
            if basePricePlus_FUT_a <= livePrice and livePrice <= basePricePlus_FUT:
                liveFuture = futureLivePrice('BANKNIFTY')
                postData = { "buy_price": liveFuture, "sell_price": (liveFuture + profitFuture), "stop_loseprice": (liveFuture - lossFuture), 'percentage': OptionId_Future, 'type': 'BUY'}
                
                if is_live_banknifty == True:
                    obj = optionFuture("BANKNIFTY", lotSizeFuture, profitFuture, lossFuture, "BUY", is_live_banknifty)
                    stock_detail.objects.create(
                    status="BUY", 
                    type= 'BUY', 
                    qty= lotSizeFuture*15, 
                    base_strike_price=nbpd['strikePrice'], 
                    live_Strike_price=livePrice, 
                    order_id = obj['orderId'], 
                    buy_price=liveFuture, 
                    sell_price = (liveFuture + profitFuture) , 
                    stop_loseprice = (liveFuture - lossFuture), 
                    percentage_id=OptionId_Future, 
                    buy_pcr = '%.2f'% (pcr) 
                    )
                else:
                    stock_detail.objects.create(
                    status="BUY", 
                    type= 'BUY', 
                    qty= lotSizeFuture*15, 
                    base_strike_price=nbpd['strikePrice'], 
                    live_Strike_price=livePrice, 
                    buy_price=liveFuture, 
                    sell_price = (liveFuture + profitFuture) , 
                    stop_loseprice = (liveFuture - lossFuture), 
                    percentage_id=OptionId_Future, 
                    buy_pcr = '%.2f'% (pcr) 
                    )
                print(f'Successfully BUY FUTURE: {postData}')


def futureSell():
    ## FUTURE SELL
    if is_op_fut_banknifty == 'FUTURE' and setBuyConditionFutureSell == True and pcr <= set_PUT_pcr:
        for bpu in base_Price_up:
            basePricePlus_PUT = bpu['strikePrice'] + basePlus_PUT
            basePricePlus_PUT_a = basePricePlus_PUT + 15
            print(f'-------------------------------------------------------------------> BANKNIFTY FUTURE SELL: {basePricePlus_PUT} < {livePrice} < {basePricePlus_PUT_a}' )
            if basePricePlus_PUT <= livePrice and livePrice <= basePricePlus_PUT_a:
                liveFuture = futureLivePrice('BANKNIFTY')
                postData = { "buy_price": liveFuture, "sell_price": (liveFuture - profitFuture), "stop_loseprice": (liveFuture + lossFuture), 'percentage': OptionId_Future, 'type': 'SELL'}
                if is_live_banknifty == True:
                    obj = optionFuture("BANKNIFTY", lotSizeFuture, profitFuture, lossFuture, "SELL", is_live_banknifty)
                    stock_detail.objects.create(
                        status="BUY", 
                        type= 'SELL', 
                        qty= lotSizeFuture*15, 
                        base_strike_price=bpu['strikePrice'], 
                        live_Strike_price=livePrice, 
                        order_id = obj['orderId'] , 
                        buy_price=liveFuture, 
                        sell_price = (liveFuture - profitFuture) , 
                        stop_loseprice = (liveFuture + lossFuture), 
                        percentage_id=OptionId_Future, 
                        buy_pcr = '%.2f'% (pcr) 
                        )
                else:
                    stock_detail.objects.create(
                    status="BUY", 
                    type= 'SELL', 
                    qty= lotSizeFuture*15, 
                    base_strike_price=bpu['strikePrice'], 
                    live_Strike_price=livePrice, 
                    buy_price=liveFuture, 
                    sell_price = (liveFuture - profitFuture) , 
                    stop_loseprice = (liveFuture + lossFuture), 
                    percentage_id=OptionId_Future, 
                    buy_pcr = '%.2f'% (pcr) 
                    )
                print(f'Successfully SELL FUTURE: {postData}')


def sell_stock_logic(stock_data, optionId, filteredData,  pcr):
    ## OPTION SELL condition
    sell_time = timezone.now()
    for i in stock_data:
        if i['status'] == 'BUY' and i['percentage_id'] == optionId:
            file = open(get_daily_log_file('banknifty'), "a")
            id = i['id'] 
            buy_price = i['buy_price'] 
            sell_price = i['sell_price']
            stop_loseprice = i['stop_loseprice']
            strikePrice = i['base_strike_price']
            if i['call_put'] == 'CALL': ce_pe = 'CE'
            elif i['call_put'] == 'PUT': ce_pe = 'PE'
            liveBidPrice = ltpData('BANKNIFTY', strikePrice, ce_pe, exprityDate)
            cLogs(file, f'BANKNIFTY {ce_pe} ---> buy_price: {buy_price} target_price: {sell_price} liveBidPrice: {liveBidPrice} stop_Losss: {stop_loseprice}')
            
            if i['admin_call'] == True:
                if buy_price < liveBidPrice:
                    final_status = 'PROFIT'
                else:
                    final_status = 'LOSS'
                stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_status, exit_pcr= '%.2f'% (pcr))
                print("SuccessFully SELL STOCK OF", ce_pe)
                cLogs(file, f'SuccessFully SELL STOCK OF {ce_pe}')
            
            if sell_price <= liveBidPrice :
                final_status = "PROFIT"
                stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_status, admin_call= True, exit_pcr= '%.2f'% (pcr))
                cLogs(file, f'SuccessFully SELL STOCK OF {ce_pe}')
            if stop_loseprice >= liveBidPrice:
                final_status = "LOSS"
                stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_status,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                cLogs(file, f'SuccessFully SELL STOCK OF {ce_pe}')


def futureExitStock():
    for sell in stock_details:
        ## FUTURE SELL
        if sell['status'] == 'BUY' and sell['percentage_id'] == OptionId_Future:
            sell_time = timezone.now()
            if sell['base_strike_price']: 
                strikePrice = sell['base_strike_price']
            else:
                strikePrice = 0
            buy_price = sell['buy_price']
            sell_price = sell['sell_price']
            stop_loseprice = sell['stop_loseprice']
            futureLive = futureLivePrice('BANKNIFTY')
            id = sell['id']
            
            if sell['type'] == 'BUY':
                consoleGreen.print(f'BANKNIFTY FUTURE BUY---> buy_price: {buy_price} target_price: {sell_price} liveBidPrice: {futureLive} stop_Losss: {stop_loseprice}')
                if sell_price <= futureLive :
                    final_status = "PROFIT"
                    stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, admin_call= True, exit_pcr= '%.2f'% (pcr))
                    print("Successfully SELL STOCK OF FUTURE")
                if stop_loseprice >= futureLive:
                    final_status = "LOSS"
                    stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                    print("Successfully SELL STOCK OF FUTURE")
                if sell['admin_call'] == True:
                    if buy_price <= futureLive:
                        final_status = 'PROFIT'
                    else:
                        final_status = 'LOSS'
                    stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, exit_pcr= '%.2f'% (pcr))
                    print("Successfully SELL STOCK OF")
            elif sell['type'] == 'SELL':
                consoleGreen.print(f'BANKNIFTY FUTURE SELL---> buy_price: {buy_price}, target_price: {sell_price}, liveBidPrice: {futureLive}, stop_Losss: {stop_loseprice}')
                if sell_price >= futureLive :
                    final_status = "PROFIT"
                    stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, admin_call= True, exit_pcr= '%.2f'% (pcr))
                    print("Successfully SELL STOCK OF FUTURE")
                if stop_loseprice <= futureLive:
                    final_status = "LOSS"
                    stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                    print("Successfully SELL STOCK OF FUTURE")
                if sell['admin_call'] == True:
                    if buy_price >= futureLive:
                        final_status = 'PROFIT'
                    else:
                        final_status = 'LOSS'
                    stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, exit_pcr= '%.2f'% (pcr))
                    print("Successfully SELL STOCK OF")