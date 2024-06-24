from datetime import datetime, time

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