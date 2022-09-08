from django.contrib import admin
from translate.models import Language,LanguagePair
# Register your models here.
admin.site.register(Language)
admin.site.register(LanguagePair)