from django.urls import path
from django.contrib import admin
from authentication.views import login, logout, change_password, list_users,add_user,update_user,delete_user

urlpatterns = [
    path('v1/login', login),
    path('v1/logout', logout),
    path('v1/user/change_password', change_password),
    path('v1/user/list', list_users),
    path('v1/user/add', add_user),
    path('v1/user/update', update_user),
    path('v1/user/delete', delete_user),
]
