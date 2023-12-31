# Generated by Django 4.2.6 on 2023-10-14 23:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(default='Chau', max_length=200)),
                ('last_name', models.CharField(default='Nguyen', max_length=200)),
                ('guest_number', models.IntegerField(default=1)),
                ('comment', models.CharField(default='Your Default Value Here', max_length=200)),
                ('reservation_date', models.DateField(blank=True, default=datetime.date(2023, 10, 14), null=True)),
                ('reservation_slot', models.SmallIntegerField(default=10)),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.IntegerField()),
                ('menu_item_description', models.TextField(max_length=1000)),
            ],
        ),
    ]
