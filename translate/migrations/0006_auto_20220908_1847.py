# Generated by Django 3.2.15 on 2022-09-08 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translate', '0005_language_other_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='src_lang',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='job',
            name='tgt_lang',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
