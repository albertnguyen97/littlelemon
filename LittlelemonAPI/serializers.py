from rest_framework import serializers
from .models import MenuItem, Category, Rating
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
    renderer_classes = [TemplateHTMLRenderer]
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
