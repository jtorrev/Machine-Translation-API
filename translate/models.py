from django.db import models
from authentication.models import MTUser

# in progress status
QUEUED = ('QUEUED', 'QUEUED')
IN_PROGRESS = ('IN_PROGRESS', 'IN_PROGRESS')
# failure status
CANCELLED = ('CANCELLED', 'CANCELLED')
ERROR = ('ERROR', 'ERROR')
# COMPLETED
COMPLETED = ('COMPLETED', 'COMPLETED')
JOB_STATUS = [QUEUED, IN_PROGRESS, CANCELLED, ERROR, COMPLETED]


class Job(models.Model):
    '''
    Model Object for Database Table
    '''
    id = models.AutoField(primary_key=True, auto_created=True, blank=False)
    name = models.CharField(max_length=100, null=False)
    status = models.CharField(max_length=100, default='PENDING', choices=JOB_STATUS)
    src_lang = models.CharField(max_length=100, null=False)
    tgt_lang = models.CharField(max_length=100, null=False)
    mtdone = models.BooleanField(null=False, default=False)
    update_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=True)

    def __str__(self):
        '''
        Method to return __str__ format of the Job Model
        '''
        return str(self.id)

    class Meta:
        '''
        Meta Sub-Class for Job Table
        '''
        db_table = "job"
        ordering = ['id', ]
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'


class Translation(models.Model):
    '''
        Model Object for Database Table
    '''
    id = models.AutoField(primary_key=True, auto_created=True, blank=False)
    sent_id = models.IntegerField(null=True)
    text = models.TextField(null=False)
    translate_text = models.TextField(null=True)
    job = models.ForeignKey(Job, null=True, on_delete=models.CASCADE)
    characters = models.IntegerField(null=False, default=0)
    src_lang = models.CharField(max_length=100, null=False)
    tgt_lang = models.CharField(max_length=100, null=False)
    user = models.ForeignKey(MTUser, null=False, on_delete=models.CASCADE)
    engine = models.TextField(null=False)
    trained_model = models.BooleanField(null=False, default=True)
    external_model = models.TextField(null=True)
    confidence = models.FloatField(null=True)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=True)

    def __str__(self):
        '''
        Method to return __str__ format of the Translation Model
        '''
        return str(self.id)

    class Meta:
        '''
        Meta Sub-Class for Translation Table
        '''
        db_table = "translation"
        ordering = ['id', ]
        verbose_name = 'Translation'
        verbose_name_plural = 'Translations'
