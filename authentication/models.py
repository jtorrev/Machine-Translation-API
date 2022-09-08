from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework import serializers
from django.utils.timezone import get_current_timezone


class MTUser(AbstractUser):
    '''
    Model Object for Database Table
    '''
    business_name = models.CharField(
        verbose_name='Business Name',
        max_length=150,
        blank=False,
        null=False,
        default="Acclaro"
    )

    def __str__(self):
        '''
        Method to return __str__ format of the Seller Model
        '''
        return str(self.username)

    def natural_key(self):
        '''
        Method to return Natural Key format of the Seller Model
        '''
        return self.__str__()

    class Meta:
        '''
        Meta Sub-Class for chapter_3_seller Table
        '''
        ordering = ['username', ]
        verbose_name = 'MTUser'
        verbose_name_plural = 'MTUsers'

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, obj):
        groups = obj.groups.all()
        if groups:
            role = groups[0].name
        else:
            role = "UNAUTHORIZED_USER"
        return role

    class Meta:
        model = MTUser
        fields = ('username',
                  'first_name',
                  'last_name',
                  'role',
                  )

