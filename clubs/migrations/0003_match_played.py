# Generated by Django 3.2.5 on 2021-12-15 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0002_auto_20211215_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='played',
            field=models.BooleanField(default=False),
        ),
    ]