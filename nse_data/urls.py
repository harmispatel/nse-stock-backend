
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views

urlpatterns = [
    path("login", views.obtain_auth_token),
    path("admin/", admin.site.urls),
    path("", include("nse_app.urls")),
    # path("__debug__/", include("debug_toolbar.urls")),

]

''' Call Function at every set time using apscheduler '''
from nse_app import jobs
jobs.start()

