from django.urls import path
from django.contrib import admin
from authentication.views import login, logout, change_password, list_users,add_user,update_user,delete_user

urlpatterns = [
    path('v1/login', login),
    path('v1/logout', logout),
    path('v1/change_password', change_password),
    path('v1/list', list_users),
    path('v1/add', add_user),
    path('v1/update', update_user),
    path('v1/delete', delete_user),
]
