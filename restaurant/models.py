from datetime import date, datetime

from django.db import models
from django.utils import timezone
# Create your models here.
class Booking(models.Model):
    first_name = models.CharField(max_length=200, default="Chau")
    last_name = models.CharField(max_length=200, default="Nguyen")
    guest_number = models.IntegerField(default=1)
    comment = models.CharField(max_length=200, default="Your Default Value Here")
    reservation_date = models.DateTimeField(default=timezone.now)
    reservation_slot = models.SmallIntegerField(default=10)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


# Add code to create a Menu model
class Menu(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField(null=False)
    menu_item_description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name
