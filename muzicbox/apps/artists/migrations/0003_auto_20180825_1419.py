# Generated by Django 2.1 on 2018-08-25 14:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0002_artist_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='background_color',
            field=models.CharField(default='#8c8c8c', help_text="Most common color for artist's background", max_length=9, validators=[django.core.validators.RegexValidator(message='Plz specify correct color', regex='^#(?:[0-9a-fA-F]{3}){1,2}$')]),
        ),
        migrations.AddField(
            model_name='artist',
            name='top_background_color',
            field=models.CharField(default='#8c8c8c', help_text="Most common color for top border in artist's page", max_length=9, validators=[django.core.validators.RegexValidator(message='Plz specify correct color', regex='^#(?:[0-9a-fA-F]{3}){1,2}$')]),
        ),
    ]
