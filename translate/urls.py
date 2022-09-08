from django.urls import path
from django.contrib import admin
from translate.views import deepl_translate
from translate.views_acclaro import xtm_translate, translate, translate_by_id, status_post, download_post

urlpatterns = [
    path('deepl', deepl_translate),
    path('xtm-translate', xtm_translate),
    path('m2-translator', translate),
    path('m2-translator-ids', translate_by_id),
    path('status/<int:id>', status_post),
    path('download/<int:id>', download_post),

]
