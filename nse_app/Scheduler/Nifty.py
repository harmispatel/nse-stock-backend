from nse_app.models import *
from django.utils import timezone
import datetime
import requests
import json
from datetime import timedelta
from rich.console import Console
from .helper import Helper
from .sell_function import sellFunOption, futureLivePrice, optionFuture, ltpData
from datetime import date, datetime as dt
import os
from dotenv import load_dotenv
from .utils import formatTime, oiDiff, formatDate, nearest_previous_15_min_from_list, getSpotPriceFromDB
from nse_app.utils import api_headers

load_dotenv()

consoleGreen = Console(style='green')
consoleRed = Console(style='red')


# VARIABLES LOCAL AND SERVER BOTH ARE SAME
NIFTY_CE = os.getenv('NIFTY_CE')
NIFTY_PE = os.getenv('NIFTY_PE')
NIFTY_FUTURE = os.getenv('NIFTY_FUTURE')

NIFTY_URL = os.getenv('NIFTY_URL')
# NIFTY_URL = https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY

SETTINGS_URL = os.getenv('SETTINGS_URL')
# SETTINGS_URL = http://zerodha.harmistechnology.com/settings


def NiftyApiFun():
    ##  Set variable as global to use across different functions 
    global api_data, livePrice, timestamp, filteredData, PEMax, CEMax, down_price, up_price, downSliceList, upSliceList, pcr, base_Price_down, base_Price_up
    global up_first_total_oi, down_first_total_oi, CEMaxValue, PEMaxValue, oi_total_call, oi_total_put, exprityDate
    
    url = NIFTY_URL
    
    try:
        api_data = requests.get(url, headers=api_headers).json()
    except Exception as e:
        consoleRed.print('ERROR IN NIFTY ------------>', 'This error is because of NSE nifty API')

    filteredData = api_data['filtered']['data']
    timestamp = api_data['records']['timestamp']
    livePrice = api_data['records']['underlyingValue']

    date_string = api_data['records']['expiryDates'][0]
    date_format = "%d-%b-%Y"
    date_object = dt.strptime(date_string, date_format).date()
    exprityDate = date(date_object.year, date_object.month, date_object.day)
    
    ## Check coustom conditions to get data from optionchain 
    down_price = Helper.downPrice(filteredData, livePrice)
    up_price = Helper.upPrice(filteredData, livePrice)
    downSliceList = Helper.downMaxValue(down_price[:-6:-1])
    upSliceList = Helper.upMaxValue(up_price[0:5])
    
    PEMax, PEMaxValue = Helper.basePriceData(down_price, downSliceList)
    CEMax, CEMaxValue = Helper.resistancePriceData(up_price, upSliceList)
    
    pcr = Helper.pcrValue(api_data)
    
    up_first_total_oi = ((up_price[0]['PE']['changeinOpenInterest'] + up_price[0]['PE']['openInterest']) - (up_price[0]['CE']['changeinOpenInterest'] + up_price[0]['CE']['openInterest']))
    down_first_total_oi = ((down_price[-1]['PE']['changeinOpenInterest'] + down_price[-1]['PE']['openInterest']) - (down_price[-1]['CE']['changeinOpenInterest'] + down_price[-1]['CE']['openInterest']))
    
    '''find call strike price for buy'''
    base_Price_down = []
    Total_oi_down_arr = []
    for downSlice3 in down_price[:-4:-1]:
        PE_oi_down = downSlice3['PE']['changeinOpenInterest'] + downSlice3['PE']['openInterest']
        CE_oi_down = downSlice3['CE']['changeinOpenInterest'] + downSlice3['CE']['openInterest']
        Total_oi_down = PE_oi_down - CE_oi_down
        Total_oi_down_arr.append(Total_oi_down)
        if Total_oi_down > oi_total_call:
            if abs(Total_oi_down_arr[0]) == abs(Total_oi_down):
                if abs(up_first_total_oi) < abs(Total_oi_down_arr[0]):
                    base_Price_down.append(downSlice3)
                    break
                else:
                    continue
            base_Price_down.append(downSlice3)
            break
    
    '''find put strike price for buy'''
    base_Price_up = []
    Total_oi_up_arr = []
    for upSlice3 in up_price[0:3]:
        PE_oi_up = upSlice3['PE']['changeinOpenInterest'] + upSlice3['PE']['openInterest']
        CE_oi_up = upSlice3['CE']['changeinOpenInterest'] + upSlice3['CE']['openInterest']
        Total_oi_up = PE_oi_up - CE_oi_up
        Total_oi_up_arr.append(Total_oi_up)
        if abs(Total_oi_up) > oi_total_put and Total_oi_up < 0:
            if abs(Total_oi_up_arr[0]) == abs(Total_oi_up):
                if abs(down_first_total_oi) < abs(Total_oi_up_arr[0]):
                    base_Price_up.append(upSlice3)  
                    break 
                else:
                    continue
            base_Price_up.append(upSlice3)  
            break 

def SettingFun():
    
    global stock_details, nseSetting, live_obj, pcr_options, oi_total_call, oi_total_put, lotSizeFuture
    global PcrObj_Call_ID, nifty_pcr_stoploss, nifty_at_set_pcr_CALL, nifty_live_pcr, PcrObj_Put_ID, nifty_pcr_stoploss_PUT, nifty_at_set_pcr_PUT
    global set_CALL_pcr, basePlus_CALL, profitPercentage_CALL, lossPercentage_CALL, lot_size_CALL, is_live_nifty, is_op_fut_nifty, lossFuture
    global set_PUT_pcr, basePlus_PUT, profitPercentage_PUT, lossPercentage_PUT, lot_size_PUT, used_logic_call, used_logic_put, profitFuture
    global OptionId_CALL, OptionId_PUT, OptionId_Future
    global setBuyCondition_CALL, setOneStock_CALL, setBuyCondition_PUT, setOneStock_PUT, setBuyCondition_PCR_CE, setBuyCondition_PCR_PUT, setBuyConditionFutureBuy, setBuyConditionFutureSell

    ## LOCAL SETTINGS 
    stock_details = stock_detail.objects.values().order_by("-buy_time")[:50]
    nseSetting = nse_setting.objects.values()
    live_obj = live.objects.values()
    pcr_options = pcr_option.objects.values()

    for pcrobj in pcr_options:
        if pcrobj['OptionName'] == 'NiftyPcrCALL':
            PcrObj_Call_ID = pcrobj['id']
            nifty_pcr_stoploss = pcrobj['PcrStopLoss']
            nifty_at_set_pcr_CALL = pcrobj['AtSetPcr']
            nifty_live_pcr = pcrobj['LivePcr']
        if pcrobj['OptionName'] == 'NiftyPcrPUT':
            PcrObj_Put_ID = pcrobj['id']
            nifty_pcr_stoploss_PUT = pcrobj['PcrStopLoss']
            nifty_at_set_pcr_PUT = pcrobj['AtSetPcr']
            nifty_live_pcr = pcrobj['LivePcr']        

    ## API SETTINGS ZERODHA HARMIS
    settings_url = SETTINGS_URL
    try:
        settings_data = requests.get(settings_url).json()
    except Exception as e:
        consoleRed.print('ERROR IN NIFTY ------------>', 'This error is because of setting API')

    settings_data_api = settings_data['data']
    is_live_nifty = settings_data['liveSettings'][0]['live_nifty']
    is_op_fut_nifty = settings_data['liveSettings'][0]['op_fut_nifty']

    for k in settings_data_api:
        if k['option'] == NIFTY_CE:
            set_CALL_pcr = k['set_pcr']
            basePlus_CALL = k['baseprice_plus']
            profitPercentage_CALL = k['profit_percentage']
            lossPercentage_CALL = k['loss_percentage']
            lot_size_CALL = k['quantity_bn']
            used_logic_call = k['used_logic']
            oi_total_call = k['oi_total']
        if k['option'] == NIFTY_PE:
            set_PUT_pcr = k['set_pcr']
            basePlus_PUT = k['baseprice_plus']
            profitPercentage_PUT = k['profit_percentage']
            lossPercentage_PUT = k['loss_percentage']
            lot_size_PUT = k['quantity_bn'] 
            used_logic_put = k['used_logic']
            oi_total_put = k['oi_total']
        if k['option'] == NIFTY_FUTURE:
            profitFuture = k['profit_percentage']
            lossFuture = k['loss_percentage']
            lotSizeFuture = k['quantity_bn'] 

    ## find ID of order in local database 
    for k in nseSetting:
        if k['option'] == NIFTY_CE:
            OptionId_CALL = k['id']
        if k['option'] == NIFTY_PE:
            OptionId_PUT = k['id']
        if k['option'] == NIFTY_FUTURE:       ## Name as per Local DB
            OptionId_Future = k['id']

    ## Check order table is exit, if not then set some field as null in variable
    if stock_details.exists():
        pass
    else:
        now = datetime.datetime.now()
        yesterday = now - timedelta(days = 1)
        stock_details = [{'percentage_id':0, "status": '', "call_put":"",'buy_time':yesterday }]

    ## CALL Buy Condition
    setBuyCondition_CALL, setOneStock_CALL = Helper.buyCondition_withOneStock(stock_details, OptionId_CALL, "CALL", "NIFTY")
    ## PUT Buy Condition
    setBuyCondition_PUT, setOneStock_PUT = Helper.buyCondition_withOneStock(stock_details, OptionId_PUT, "PUT", "NIFTY")
    ## FUTURE BUY Condition
    setBuyConditionFutureBuy = Helper.buyConditionFuture(stock_details, OptionId_Future, 'BUY')
    ## FUTURE SELL Condition
    setBuyConditionFutureSell = Helper.buyConditionFuture(stock_details, OptionId_Future, 'SELL')


def NIFTY():
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
            SettingFun()
            NiftyApiFun()

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
            # consoleRed.print('Error-->', e)
            # consoleRed.print("Connection refused by the server...................................... NIFTY")


def buyOnOptionGivenTime():
    ''' 
        Automactically buy on specific exact time
        Strike price: first In the money
    '''
    url = 'https://nseindia.harmistechnology.com/api/currentDateGrah'
    isBuyCondition = Helper.isBuyCondition(stock_details, OptionId_CALL)

    if isBuyCondition == True:
        try:
            response = requests.post(url, {
                "date": formatDate(today)
            }).json()
        except Exception as e:
            consoleRed.print('ERROR IN NIFTY ------------>', 'This error is because of currentDateGrah API')        

        if response['success'] == True:
            for data in response['data']['data']:
                end_time = formatTime(data['end_time'])
                print('Nifty -------->', end_time, '==',  formatTime(current_time))
                
                if end_time == formatTime(current_time) and data['featureby_or_optionby'] == 'Option' and (data['nifty_or_banknifty'] == 'NIFTY' or data['nifty_or_banknifty'] == 'Both'):
                    file = open("nifty_logs.txt", "a")
                    file.write(f'-------------> NIFTY BUYING ON {today.date()} at {end_time} \n')                   
                    if  data['buy_or_sale'] != 'BUY' or 'SELL': 
                        nearest_previous_15_min = nearest_previous_15_min_from_list(formatTime(current_time))
                        if nearest_previous_15_min != None:
                            record_given_time, record_15_min_before = getSpotPriceFromDB(nearest_previous_15_min, 'NIFTY', pcr_values)
                            if record_given_time is not None and record_15_min_before is not None:
                                if record_given_time.live_price > record_15_min_before.live_price:
                                    data['buy_or_sale'] = 'SELL'
                                else:
                                    data['buy_or_sale'] = 'BUY'

                    bidPrice = 0
                    if data['buy_or_sale'] == 'BUY':
                        call_or_put = 'CALL'
                        OptionId = OptionId_CALL
                        strikeData = down_price[-1]
                        strikePrice = strikeData['strikePrice']
                        bidPrice = ltpData('NIFTY', strikePrice, 'CE', exprityDate)
                        targetPrice = bidPrice + int(data['target_price'])
                        stopLossPrice = bidPrice - (int(data['target_price']) / 2)
                        file.write(f'{call_or_put} BUY -> strikePrice: {strikePrice}, bidPrice: {bidPrice} \n')                   
                    if data['buy_or_sale'] == 'SELL':
                        call_or_put = 'PUT'
                        OptionId = OptionId_PUT
                        strikeData = up_price[0]
                        strikePrice = strikeData['strikePrice']
                        bidPrice = ltpData('NIFTY', strikePrice, 'PE', exprityDate)
                        targetPrice = bidPrice + int(data['target_price'])
                        stopLossPrice = bidPrice - (int(data['target_price']) / 2)
                        file.write(f'{call_or_put} BUY -> strikePrice: {strikePrice}, bidPrice: {bidPrice} \n')  
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
                        file.write(f'Trade is place at price {bidPrice} on {today.date()} {end_time} \n')
                        if is_live_nifty == True:
                            sellFunOption(strikePrice, bidPrice, data['target_price'], str(int(data['target_price']) / 2), OptionId_CALL, data['quantity'], sell_data.id, exprityDate)    
                            file.write(f'SUCCESS BUY in live broker {bidPrice} on {today} {end_time} \n')
                        consoleGreen.print(f'NIFTY SUCCESS BUY AT: {end_time} -> buyPrice: {bidPrice}')
                        break
        else:
            consoleRed.print('Error is in api, Please check -> "currentDateGrah" API')

def sell_stock_logic(stock_data, optionId, filteredData,  pcr):
    ## OPTION SELL condition
    sell_time = timezone.now()
    for i in stock_data:
        if i['status'] == 'BUY' and i['percentage_id'] == optionId:
            id = i['id'] 
            buy_price = i['buy_price'] 
            sell_price = i['sell_price']
            stop_loseprice = i['stop_loseprice']
            strikePrice = i['base_strike_price']
            if i['call_put'] == 'CALL': ce_pe = 'CE'
            elif i['call_put'] == 'PUT': ce_pe = 'PE'
            liveBidPrice = ltpData('NIFTY', strikePrice, ce_pe, exprityDate)
            
            print('NIFTY', ce_pe, '--->', 'buy_price:', buy_price, 'target_price:', sell_price, 'liveBidPrice:', liveBidPrice, 'stop_Losss:', stop_loseprice)
            if i['admin_call'] == True:
                if buy_price < liveBidPrice:
                    final_status = 'PROFIT'
                else:
                    final_status = 'LOSS'
                stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = liveBidPrice, oi_diff = oiDiff(filteredData, strikePrice), sell_buy_time=sell_time, final_status = final_status, exit_pcr= '%.2f'% (pcr))
                print("SuccessFully SELL STOCK OF", ce_pe)
            
            if sell_price <= liveBidPrice :
                final_status = "PROFIT"
                stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = liveBidPrice, oi_diff = oiDiff(filteredData, strikePrice), sell_buy_time=sell_time, final_status = final_status, admin_call= True, exit_pcr= '%.2f'% (pcr))
                print("SuccessFully SELL STOCK OF",ce_pe)
            if stop_loseprice >= liveBidPrice:
                final_status = "LOSS"
                stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = liveBidPrice, oi_diff = oiDiff(filteredData, strikePrice), sell_buy_time=sell_time, final_status = final_status,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                print("SuccessFully SELL STOCK OF", ce_pe)


def callBuy():
    ### CALL BUY
    if is_op_fut_nifty == 'OPTION' and setOneStock_CALL == True and setBuyCondition_CALL == True and pcr >= set_CALL_pcr:
        for nbpd in base_Price_down:
            call_call = "CALL"
            basePricePlus_CALL = nbpd['strikePrice'] + basePlus_CALL
            basePricePlus_CALL_a = basePricePlus_CALL - 15
            print('-------------------------------------------------------------------> NIFTY CE:', basePricePlus_CALL_a,'<', livePrice,'<', basePricePlus_CALL)
            if basePricePlus_CALL_a <= livePrice and livePrice <= basePricePlus_CALL:
                BidPrice_CE = nbpd['CE']['bidprice']
                strikePrice_CE = nbpd['strikePrice']
                squareoff_CE = '%.2f'% (( BidPrice_CE * profitPercentage_CALL ) / 100)
                stoploss_CE = '%.2f'% ((BidPrice_CE * lossPercentage_CALL ) / 100)
                sellPrice_CE = '%.2f'% ((BidPrice_CE * profitPercentage_CALL) / 100 + BidPrice_CE)
                stop_loss_CE = '%.2f'% (BidPrice_CE - (BidPrice_CE * lossPercentage_CALL ) / 100)
                
                postData = { "buy_price": BidPrice_CE, "base_strike_price":strikePrice_CE, "live_Strike_price":livePrice, "sell_price": sellPrice_CE, "stop_loseprice": stop_loss_CE, 'percentage': OptionId_CALL, 'call_put':call_call}
                obj_banknifty_old = stock_detail.objects.create(status="BUY",qty = lot_size_CALL*50 ,buy_price = BidPrice_CE, base_strike_price=strikePrice_CE, live_Strike_price=livePrice, live_brid_price=BidPrice_CE, sell_price= sellPrice_CE ,stop_loseprice=stop_loss_CE, percentage_id=OptionId_CALL , call_put =call_call, buy_pcr = '%.2f'% (pcr) )
                
                if is_live_nifty == True:
                    sellFunOption(strikePrice_CE, BidPrice_CE, squareoff_CE, stoploss_CE, OptionId_CALL, lot_size_CALL, obj_banknifty_old.id, exprityDate)
                print('SuccessFully Buy IN NIFTY CALL: ', postData)    


def putBuy():
    ### PUT BUY
    if is_op_fut_nifty == 'OPTION' and setOneStock_PUT == True and setBuyCondition_PUT == True and pcr <= set_PUT_pcr:
        for bpu in base_Price_up:
                put_put = "PUT"
                basePricePlus_PUT = bpu['strikePrice'] + basePlus_PUT
                basePricePlus_PUT_a = basePricePlus_PUT + 15
                print('-------------------------------------------------------------------> NIFTY PE:',basePricePlus_PUT_a, '<', livePrice, '<', basePricePlus_PUT )
                if basePricePlus_PUT <= livePrice and livePrice <= basePricePlus_PUT_a:
                    BidPrice_PUT = bpu['PE']['bidprice']
                    strikePrice_PUT = bpu['strikePrice']
                    squareoff_PUT = '%.2f'% (( BidPrice_PUT * profitPercentage_PUT ) / 100)
                    stoploss_PUT = '%.2f'% ((BidPrice_PUT * lossPercentage_PUT ) / 100)
                    sellPrice_PUT = '%.2f'% ((BidPrice_PUT * profitPercentage_PUT) / 100 + BidPrice_PUT)
                    stop_loss_PUT = '%.2f'% (BidPrice_PUT - (BidPrice_PUT * lossPercentage_PUT ) / 100)
                    
                    obj_banknifty_old = stock_detail.objects.create(status="BUY", qty = lot_size_PUT*50, buy_price = BidPrice_PUT,live_brid_price=BidPrice_PUT , base_strike_price=strikePrice_PUT, live_Strike_price=livePrice, sell_price= sellPrice_PUT ,stop_loseprice=stop_loss_PUT, percentage_id=OptionId_PUT , call_put =put_put, buy_pcr = '%.2f'% (pcr) )
                    postData = { "buy_price": BidPrice_PUT, "base_strike_price":strikePrice_PUT, "live_Strike_price":livePrice, "sell_price": sellPrice_PUT, "stop_loseprice": stop_loss_PUT, 'percentage': OptionId_PUT, 'call_put':put_put}
                    
                    if is_live_nifty == True:
                        sellFunOption(strikePrice_PUT, BidPrice_PUT, squareoff_PUT, stoploss_PUT, OptionId_PUT, lot_size_PUT, obj_banknifty_old.id, exprityDate)
                    print('SuccessFully Buy IN NIFTY PUT: ',postData)
            

def futureBuy():
    ## FUTURE BUY
    if is_op_fut_nifty == 'FUTURE' and setBuyConditionFutureBuy == True and pcr >= set_CALL_pcr:
        for nbpd in base_Price_down:
            basePricePlus_FUT = nbpd['strikePrice'] + basePlus_CALL
            basePricePlus_FUT_a = basePricePlus_FUT - 15
            print('-------------------------------------------------------------------> NIFTY FUTURE BUY:', basePricePlus_FUT_a,'<', livePrice,'<', basePricePlus_FUT)
            if basePricePlus_FUT_a <= livePrice and livePrice <= basePricePlus_FUT:
                liveFuture = futureLivePrice('NIFTY')
                postData = { "buy_price": liveFuture, "sell_price": (liveFuture + profitFuture), "stop_loseprice": (liveFuture - lossFuture), 'percentage': OptionId_Future, 'type': 'BUY'}
                
                if is_live_nifty == True:
                    obj = optionFuture("NIFTY", lotSizeFuture, profitFuture, lossFuture, "BUY", is_live_nifty)
                    stock_detail.objects.create(status="BUY", qty = lotSizeFuture*50, base_strike_price=nbpd['strikePrice'], type= 'BUY', live_Strike_price=livePrice, order_id = obj['orderId'] , buy_price=liveFuture, sell_price = (liveFuture + profitFuture) , stop_loseprice = (liveFuture - lossFuture), percentage_id=OptionId_Future, buy_pcr = '%.2f'% (pcr) )
                else:
                    stock_detail.objects.create(status="BUY", qty = lotSizeFuture*50, type= 'BUY', base_strike_price=nbpd['strikePrice'], live_Strike_price=livePrice, buy_price=liveFuture, sell_price = (liveFuture + profitFuture) , stop_loseprice = (liveFuture - lossFuture), percentage_id=OptionId_Future, buy_pcr = '%.2f'% (pcr) )
                print('Successfully BUY FUTURE: ', postData)
            

def futureSell():
    ## FUTURE SELL
    if is_op_fut_nifty == 'FUTURE' and setBuyConditionFutureSell == True and pcr <= set_PUT_pcr:
        for bpu in base_Price_up:
            basePricePlus_PUT = bpu['strikePrice'] + basePlus_PUT
            basePricePlus_PUT_a = basePricePlus_PUT + 15
            print('-------------------------------------------------------------------> NIFTY FUTURE SELL:',basePricePlus_PUT, '<', livePrice, '<', basePricePlus_PUT_a )
            if basePricePlus_PUT <= livePrice and livePrice <= basePricePlus_PUT_a:
                liveFuture = futureLivePrice('NIFTY')
                postData = { "buy_price": liveFuture, "sell_price": (liveFuture - profitFuture), "stop_loseprice": (liveFuture + lossFuture), 'percentage': OptionId_Future, 'type': 'SELL'}
                if is_live_nifty == True:
                    obj = optionFuture("NIFTY", lotSizeFuture, profitFuture, lossFuture, "SELL", is_live_nifty)
                    stock_detail.objects.create(status="BUY", qty = lotSizeFuture*50, type= 'SELL', base_strike_price=bpu['strikePrice'], live_Strike_price=livePrice, order_id = obj['orderId'] , buy_price=liveFuture, sell_price = (liveFuture - profitFuture) , stop_loseprice = (liveFuture + lossFuture), percentage_id=OptionId_Future, buy_pcr = '%.2f'% (pcr) )
                else:
                    stock_detail.objects.create(status="BUY", qty = lotSizeFuture*50, type= 'SELL', base_strike_price=bpu['strikePrice'], live_Strike_price=livePrice, buy_price=liveFuture, sell_price = (liveFuture - profitFuture) , stop_loseprice = (liveFuture + lossFuture), percentage_id=OptionId_Future, buy_pcr = '%.2f'% (pcr) )                        
                print('Successfully SELL FUTURE: ', postData)
            

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
            futureLive = futureLivePrice('NIFTY')
            id = sell['id']
            
            if sell['type'] == 'BUY':
                consoleGreen.print('NIFTY FUTURE BUY--->', 'buy_price:', buy_price, 'target_price:', sell_price, 'liveBidPrice:', futureLive, 'stop_Losss:', stop_loseprice)
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
                consoleGreen.print('NIFTY FUTURE SELL--->', 'buy_price:', buy_price, 'target_price:', sell_price, 'liveBidPrice:', futureLive, 'stop_Losss:', stop_loseprice)
                if sell_price >= futureLive :
                    final_status = "PROFIT"
                    stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, admin_call= True, exit_pcr= '%.2f'% (pcr))
                    print("Successfully SELL STOCK OF FUTURE")
                if stop_loseprice <= futureLive:
                    final_status = "LOSS"
                    stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                    print("Successfully SELL STOCK OF FUTURE")
                if sell['admin_call'] == True:
                    if buy_price > futureLive:
                        final_status = 'PROFIT'
                    else:
                        final_status = 'LOSS'
                    stock_detail.objects.filter(id=id).update(status = 'SELL', oi_diff = oiDiff(filteredData, strikePrice), exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, exit_pcr= '%.2f'% (pcr))
                    print("Successfully SELL STOCK OF")