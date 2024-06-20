from dotenv import load_dotenv
import os
load_dotenv()

BANKNIFTY_URL = os.getenv('BANKNIFTY_URL')
NIFTY_URL = os.getenv('NIFTY_URL')

TIMES_5_MIN = [
    '09:15',
    '09:20','09:25','09:30',
    '09:35','09:40','09:45',
    '09:50','09:55','10:00',
    '10:05','10:10','10:15',
    '10:20','10:25','10:30',
    '10:35','10:40','10:45',
    '10:50','10:55','11:00',
    '11:05','11:10','11:15',
    '11:20','11:25','11:30',
    '11:35','11:40','11:45',
    '11:50','11:55','12:00',
    '12:05','12:10','12:15',
    '12:20','12:25','12:30',
    '12:35','12:40','12:45',
    '12:50','12:55','13:00',
    '13:05','13:10','13:15',
    '13:20','13:25','13:30',
    '13:35','13:40','13:45',
    '13:50','13:55','14:00',
    '14:05','14:10','14:15',
    '14:20','14:25','14:30',
    '14:35','14:40','14:45',
    '14:50','14:55','15:00',
    '15:05','15:10','15:15',
    '15:20','15:25','15:30',
]

TIMES_15_MIN = [
    '09:00', '09:15', '09:30', '09:45', 
    '10:00', '10:15', '10:30', '10:45', 
    '11:00', '11:15', '11:30', '11:45', 
    '12:00', '12:15', '12:30', '12:45', 
    '13:00', '13:15', '13:30', '13:45', 
    '14:00', '14:15', '14:30', '14:45', 
    '15:00', '20:00'
]


api_headers =  {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
    'like Gecko) '
    'Chrome/80.0.3987.149 Safari/537.36',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'
}



INTRA_VALUE = [
  {
    "id": 53,
    "intraday_id": 28,
    "start_time": "11:41:00",
    "end_time": "12:41:00",
    "buy_or_sale": "BUY",
    "nifty_or_banknifty": "BankNifty",
    "featureby_or_optionby": "Future",
    "quantity": 23,
    "created_at": "2024-06-11 09:12:25",
    "updated_at": "2024-06-11 09:12:25"
  },
  {
    "id": 54,
    "intraday_id": 28,
    "start_time": "12:41:00",
    "end_time": "13:41:00",
    "buy_or_sale": "SELL",
    "nifty_or_banknifty": "Nifty",
    "featureby_or_optionby": "Option",
    "quantity": 1,
    "created_at": "2024-06-11 09:12:25",
    "updated_at": "2024-06-11 09:12:25"
  },
  {
    "id": 55,
    "intraday_id": 28,
    "start_time": "12:41:00",
    "end_time": "14:44:00",
    "buy_or_sale": "BUY",
    "nifty_or_banknifty": "Both",
    "featureby_or_optionby": "Future",
    "quantity": 23,
    "created_at": "2024-06-11 09:12:25",
    "updated_at": "2024-06-11 09:12:25"
  },
  {
    "id": 57,
    "intraday_id": 28,
    "start_time": "12:10:00",
    "end_time": "14:00:00",
    "buy_or_sale": "BUY",
    "nifty_or_banknifty": "Nifty",
    "featureby_or_optionby": "Option",
    "quantity": 1,
    "created_at": "2024-06-12 05:37:54",
    "updated_at": "2024-06-12 05:40:59"
  },
  {
    "id": 58,
    "intraday_id": 28,
    "start_time": "12:11:00",
    "end_time": "12:11:00",
    "buy_or_sale": "SELL",
    "nifty_or_banknifty": "BankNifty",
    "featureby_or_optionby": "Future",
    "quantity": 33,
    "created_at": "2024-06-12 05:41:35",
    "updated_at": "2024-06-12 05:41:35"
  },
  {
    "id": 59,
    "intraday_id": 30,
    "start_time": "12:31:00",
    "end_time": "11:31:00",
    "buy_or_sale": "BUY",
    "nifty_or_banknifty": "BankNifty",
    "featureby_or_optionby": "Future",
    "quantity": 3,
    "created_at": "2024-06-12 06:01:41",
    "updated_at": "2024-06-12 06:01:41"
  },
  {
    "id": 60,
    "intraday_id": 30,
    "start_time": "12:31:00",
    "end_time": "13:31:00",
    "buy_or_sale": "SELL",
    "nifty_or_banknifty": "Both",
    "featureby_or_optionby": "Option",
    "quantity": 12,
    "created_at": "2024-06-12 06:01:41",
    "updated_at": "2024-06-12 06:01:41"
  }
]