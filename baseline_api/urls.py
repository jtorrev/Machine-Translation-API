from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('b', admin.site.urls),
]