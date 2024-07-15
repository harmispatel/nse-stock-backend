from datetime import datetime, time
from nse_app.utils import TIMES_15_MIN
from django.utils import timezone
from datetime import timedelta
from django.db.models import QuerySet
from nse_app.models import pcr_values

def formatTime(time_input):
    ''' return time in HH:MM format '''
    if isinstance(time_input, str):
        time_object = datetime.strptime(time_input, "%H:%M:%S")
    elif isinstance(time_input, datetime):
        time_object = time_input
    elif isinstance(time_input, time):
        time_object = time_input
    formatted_time = time_object.strftime("%H:%M")
    return formatted_time

def formatDate(dataString):
    ''' return date in YY-MM-DD format '''
    formatted_date = dataString.strftime('%Y-%m-%d')
    return formatted_date



def oiDiff(filteredData, strikePrice):
    ## Find and calculate OIdifferance from filteredData
    for i in filteredData:
        if strikePrice == i['strikePrice']:
            return (i['PE']['changeinOpenInterest'] + i['PE']['openInterest']) - (i['CE']['changeinOpenInterest'] + i['CE']['openInterest'])
        if strikePrice == 0:
            return 0
        

def nearest_previous_15_min_from_list(time_str):
    time = datetime.strptime(time_str, "%H:%M")
    
    previous_times = [t for t in TIMES_15_MIN if datetime.strptime(t, "%H:%M") <= time]
    
    return max(previous_times, default=None)


def getSpotPriceFromDB(given_time, option, pcr_values: QuerySet[pcr_values]) -> QuerySet[pcr_values]:
    today_date = datetime.today().date()
    # date =  datetime(2024, 6, 29).date()
    target_datetime_naive = datetime.combine(today_date, datetime.strptime(given_time, "%H:%M").time())

    target_datetime = timezone.make_aware(target_datetime_naive, timezone.get_default_timezone())
    target_datetime_15_min_before = target_datetime - timedelta(minutes=15)

    start_time = target_datetime
    end_time = target_datetime + timedelta(minutes=1)
    start_time_15_min_before = target_datetime_15_min_before
    end_time_15_min_before = start_time_15_min_before + timedelta(minutes=1)
    record_given_time = pcr_values.objects.filter(
        option_name=option, 
        timestamp__gte=start_time, 
        timestamp__lt=end_time
    ).first()
    record_15_min_before = pcr_values.objects.filter(
        option_name=option, 
        timestamp__gte=start_time_15_min_before, 
        timestamp__lt=end_time_15_min_before
    ).first()

    return record_given_time, record_15_min_before