
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views

from apscheduler.schedulers.background import BackgroundScheduler
from nse_app.Scheduler.bank_nifty import BANKNIFTY
from nse_app.Scheduler.nifty import NIFTY
from nse_app.Scheduler.pcr_values import PcrValues
from nse_app.Scheduler.stock import stockFutureSell


urlpatterns = [
    path("login", views.obtain_auth_token),
    path("admin/", admin.site.urls),
    path("", include("nse_app.urls")),
    # path("__debug__/", include("debug_toolbar.urls")),

]

''' Call Function at every set time using apscheduler '''

scheduler = BackgroundScheduler()
scheduler.add_job(stockFutureSell, "interval", minutes=0.27, id='StockFuture')
scheduler.add_job(PcrValues, "interval", minutes=1, id='PcrValues_001')
scheduler.add_job(NIFTY, "interval", minutes=0.27, id='nifty_001',) 
scheduler.add_job(BANKNIFTY, "interval", minutes=0.27, id='banknifty_001')
scheduler.start()
