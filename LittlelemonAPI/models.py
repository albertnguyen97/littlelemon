from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1)

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu items'

    def __str__(self):
        return self.title


class Rating(models.Model):
    menuitem_id = models.SmallIntegerField()
    rating = models.SmallIntegerField()
    category = models.ForeignKey(User, on_delete=models.CASCADE)


# limit = request.GET.get(‘limit’)
# MenuItem.objects.raw('SELECT * FROM LittleLemonAPI_menuitem LIMIT %s', [limit])


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        unique_together = ('menuitem', 'user')

    def __str__(self):
        return self.user


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_as_delivery_crew')
    is_shipped = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=6, decimal_places=2)

    shipping_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    date = models.DateTimeField(db_index=True)

    def __str__(self):
        return f"Order {self.pk} by {self.user.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order', 'menuitem')

    def __str__(self):
        return self.order

