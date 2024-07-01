from apscheduler.schedulers.background import BackgroundScheduler
from nse_app.Scheduler.bank_nifty import BANKNIFTY
from nse_app.Scheduler.Nifty import NIFTY
from nse_app.Scheduler.pcr_values import PcrValues
from nse_app.Scheduler.Stock import stockFutureSell

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(BANKNIFTY, "interval", minutes=0.27, id='banknifty_001')
    scheduler.add_job(NIFTY, "interval", minutes=0.27, id='nifty_001')
    scheduler.add_job(PcrValues, "interval", minutes=1, id='PcrValues_001')
    scheduler.add_job(stockFutureSell, "interval", minutes=0.27, id='StockFuture')
    scheduler.start()