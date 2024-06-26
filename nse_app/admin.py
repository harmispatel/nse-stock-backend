from django.contrib import admin
from .models import *
from import_export.admin import ExportActionMixin
from import_export.widgets import ForeignKeyWidget


from import_export import resources, fields
@admin.register(nse_setting)
class nsesetting(admin.ModelAdmin):
    list_display = ['option', 'profit_percentage', 'loss_percentage', 'set_pcr', 'baseprice_plus' ]

@admin.register(pcr_values)
class pcr_values(admin.ModelAdmin):
    list_display = ['option_name', 'pcr_value', 'live_price', 'timestamp' ]


class StockDetailResource(resources.ModelResource):
    percentage = fields.Field(
        column_name='percentage',
        attribute='percentage',
        widget=ForeignKeyWidget(nse_setting, 'option')  
    )

    class Meta:
        model = stock_detail


@admin.register(stock_detail)
class nsestock(ExportActionMixin, admin.ModelAdmin):
    list_display = ['percentage', 'base_strike_price', 'buy_price', 'exit_price', 'buy_time', 'final_status', 'stock_name']
    resource_class = StockDetailResource
    
@admin.register(pcr_stock_name)
class pcrstock(admin.ModelAdmin):
    list_display = ['name', 'pcr', 'date']

@admin.register(live)
class live(admin.ModelAdmin):
    list_display = ['live_banknifty', 'live_nifty', 'live_stock_ce', 'live_stock_pe']

@admin.register(pcr_option)
class live(admin.ModelAdmin):
    list_display = ['OptionName', 'AtSetPcr', 'PcrStopLoss', 'LivePcr']

@admin.register(AccountCredential)
class live(admin.ModelAdmin):
    list_display = ['username', 'apikey', 'password', 't_otp']