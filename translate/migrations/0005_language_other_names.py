# Generated by Django 3.2.15 on 2022-09-08 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translate', '0004_translation'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='other_names',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
