from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('a', admin.site.urls),
]