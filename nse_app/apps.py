from django.apps import AppConfig


class NseAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nse_app'
    
    # def ready(self):
    #     from nse_app import jobs
    #     jobs.start()
    #     print('Jobs started ....')