from datetime import datetime
from rest_framework import serializers
from .models import MenuItem, Category, Rating, Order, OrderItem, Cart
from decimal import Decimal
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
import bleach
from django.contrib.auth.models import User

# from rest_framework.validators import UniqueTogetherValidator


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.HyperlinkedModelSerializer):
    # renderer_classes = [TemplateHTMLRenderer]
    price = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=2)
    title = serializers.CharField(
        max_length=255,
        validators=[UniqueValidator(queryset=MenuItem.objects.all())]
    )
    stock = serializers.IntegerField(source='inventory')
    price_after_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    def validate_title(self, value):
        return bleach.clean(value)

    # def validate(self, attrs):
    #     attrs['title'] = bleach.clean(attrs['title'])
    #
    #     if (attrs['price'] < 2):
    #         raise serializers.ValidationError('Price should not be less than 2.0')
    #     if (attrs['inventory'] < 0):
    #         raise serializers.ValidationError('Stock cannot be negative')
    #     return super().validate(attrs)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'stock', 'price_after_tax', 'category', 'category_id']
        depth = 1
        extra_kwarg = {
            # 'price': {'min_value': 2},
            'stock': {'source': 'inventory', 'min_value': 0},
            'title': {
                'validators': [
                    UniqueValidator(
                        queryset=MenuItem.objects.all()
                    )
                ]
            }
        }
        # validators = [
        #     UniqueTogetherValidator(
        #     queryset = MenuItem.objects.all(),
        #     fields = ['title', 'price']
        #       ),
        # ]
        # def validate_price(self, value):
        #     if (value < 2):
        #         raise serializers.ValidationError('Price should not be less than 2.0')
        #
        #
        # def validate_stock(self, value):
        #     if (value < 0):
        #         raise serializers.ValidationError('Stock cannot be negative')

        def validate(self, attrs):
            if (attrs['price'] < 2):
                raise serializers.ValidationError('Price should not be less than 2.0')

            if (attrs['inventory'] < 0):
                raise serializers.ValidationError('Stock cannot be negative')
            return super().validate(attrs)

    @staticmethod
    def calculate_tax(product: MenuItem):
        return round(product.price * Decimal(1.1), 2)


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Rating
        fields = ['user', 'menuitem_id', 'rating']

    validators = [
        UniqueTogetherValidator(
            queryset=Rating.objects.all(),
            fields=['user', 'menuitem_id']
        )
    ]

    extra_kwargs = {
        'rating': {'min_value': 0, 'max_value':5},
    }


class UserSerializer(serializers.ModelSerializer):
    Date_Joined = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(write_only=True, default=datetime.now)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'Date_Joined']

    def get_Date_Joined(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d')


class UserCartSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source='menuitem.price', read_only=True)
    name = serializers.CharField(source='menuitem.title', read_only=True)

    class Meta:
        model = Cart
        fields = ['user_id', 'menuitem', 'name', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'price': {'read_only': True}
        }


class OrderItemSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source='menuitem.price', read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    name = serializers.CharField(source='menuitem.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['name', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'menuitem': {'read_only': True}
        }


class UserOrdersSerializer(serializers.ModelSerializer):
    Date = serializers.SerializerMethodField()
    date = serializers.DateTimeField(write_only=True, default=datetime.now)
    order_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'Date', 'date', 'order_items']
        extra_kwargs = {
            'total': {'read_only': True}
        }

    def get_Date(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    def get_order_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializer = OrderItemSerializer(order_items, many=True, context={'request': self.context['request']})
        return serializer.data