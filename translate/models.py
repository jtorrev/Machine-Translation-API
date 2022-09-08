from django.db import models
from authentication.models import MTUser

PENDING = ('PENDING', 'PENDING')
IN_PROGRESS = ('IN_PROGRESS', 'IN_PROGRESS')
COMPLETED = ('COMPLETED', 'COMPLETED')
JOB_STATUS = [PENDING, IN_PROGRESS, COMPLETED]


class Language(models.Model):
    '''
    Model Object for Database Table
    '''
    id = models.AutoField(primary_key=True, auto_created=True, blank=False)
    name = models.CharField(max_length=100, null=False)
    name_iso_639_1 = models.CharField(max_length=2, null=False)
    name_iso_639_2 = models.CharField(max_length=3, null=False)
    other_names = models.CharField(max_length=100, null=False)

    def __str__(self):
        '''
        Method to return __str__ format of the Language Model
        '''
        return str("{} ({})".format(self.name, self.name_iso_639_1))

    class Meta:
        '''
        Meta Sub-Class for Language Table
        '''
        db_table = "language"
        ordering = ['name', ]
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'


class LanguagePair(models.Model):
    '''
    Model Object for Database Table
    '''
    id = models.AutoField(primary_key=True, auto_created=True, blank=False)
    src_lang = models.ForeignKey(Language, null=False, on_delete=models.CASCADE, related_name='src_lang')
    tgt_lang = models.ForeignKey(Language, null=False, on_delete=models.CASCADE, related_name='tgt_lang')

    # engine = models.CharField(max_length=100, null=False)
    # engine_dir = models.FilePathField(max_length=100, null=False,allow_files=False, allow_folders=True)

    def __str__(self):
        '''
        Method to return __str__ format of the Language Model
        '''
        return str("{} --> {}".format(self.src_lang.name, self.tgt_lang.name))

    class Meta:
        '''
        Meta Sub-Class for Language Table
        '''
        db_table = "language_pair"
        ordering = ['id', ]
        verbose_name = 'Language Pair'
        verbose_name_plural = 'Language Pairs'


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
    lang_pair = models.ForeignKey(LanguagePair, null=False, on_delete=models.CASCADE)
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
