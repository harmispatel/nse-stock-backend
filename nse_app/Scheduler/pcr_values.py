import requests
import json
from datetime import datetime
from nse_app.models import *
from .helper import Helper
from nse_app.utils import TIMES_15_MIN, api_headers, BANKNIFTY_URL, NIFTY_URL

def PcrValues():
    current_time = datetime.now()
    current_time = current_time.strftime("%H:%M")    
    
    try:
        ## BANKNIFTY PCR and LIVE PRICE
        if current_time in TIMES_15_MIN:
            url = BANKNIFTY_URL
            response = requests.get(url, headers=api_headers)
            data = response.text
            api_data = json.loads(data)
            
            pcr = Helper.pcrValue(api_data)
            livePrice = api_data['records']['underlyingValue']
            pcr_values.objects.create(option_name='BANKNIFTY', pcr_value=pcr, live_price=livePrice)
            print('Pcr BankNifty->', pcr)

        ## NIFTY PCR and LIVE PRICE
        if current_time in TIMES_15_MIN:
            url_nifty = NIFTY_URL
            response_nifty = requests.get(url_nifty, headers=api_headers)
            data_nifty = response_nifty.text
            api_data_nifty = json.loads(data_nifty)
            pcr_nifty = Helper.pcrValue(api_data_nifty)
            livePriceNifty = api_data['records']['underlyingValue']
            pcr_values.objects.create(option_name='NIFTY', pcr_value=pcr_nifty, live_price=livePriceNifty)
            print('Pcr Nifty->', pcr_nifty)
            
    except Exception as e:
        print(e)



    # ## LIVE PRICE BANKNIFTY
    # livePrice_banknifty = api_data['records']['underlyingValue']
    # base_zone_obj = BaseZoneBanknifty.objects.all().values() 
    # resistance_zone_obj = ResistanceZone_Banknifty.objects.all().values() 
    # if len(base_zone_obj) != 0:
    #     if base_zone_obj[0]['in_basezone'] == True:
    #         if current_time in times:
    #             LiveDataBankNifty.objects.create(live_price = livePrice_banknifty, in_basezone=True)
    #             print("LiveData Added successfully BankNifty", livePrice_banknifty)
    
    # elif len(resistance_zone_obj) != 0:
    #     if resistance_zone_obj[0]['in_resistance'] == True:
    #         if current_time in times:
    #             LiveDataBankNifty.objects.create(live_price = livePrice_banknifty, in_resistance=True)
    #             print("LiveData Added successfully BankNifty", livePrice_banknifty)
    # else:
    #     if current_time in times:
    #         LiveDataBankNifty.objects.create(live_price = livePrice_banknifty)
    #         print(current_time in times)
    #         print("LiveData Added successfully BankNifty", livePrice_banknifty)



        
    # ## LIVE PRICE NIFTY
    # livePrice_nifty = api_data_nifty['records']['underlyingValue']
    # base_zone_obj_nifty = BaseZoneNifty.objects.all().values() 
    # resistance_zone_obj_nifty = ResistanceZone_Nifty.objects.all().values() 
    # if len(base_zone_obj_nifty) != 0:
    #     if base_zone_obj_nifty[0]['in_basezone'] == True:
    #         if current_time in times:
    #             LiveDataNifty.objects.create(live_price = livePrice_nifty, in_basezone=True)
    #             print("LiveData Added successfully Nifty", livePrice_nifty)

    # elif len(resistance_zone_obj_nifty) != 0:
    #     if resistance_zone_obj_nifty[0]['in_resistance'] == True:
    #         if current_time in times:
    #             LiveDataNifty.objects.create(live_price = livePrice_nifty, in_resistance=True)
    #             print("LiveData Added successfully Nifty", livePrice_nifty)
        
    # else:
    #     if current_time in times:
    #         LiveDataNifty.objects.create(live_price = livePrice_nifty)
    #         print(current_time in times)
    #         print("LiveData Added successfully Nifty", livePrice_nifty)
