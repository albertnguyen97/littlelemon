from _decimal import Decimal

from django.shortcuts import render, get_object_or_404
from rest_framework import generics, filters, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from .models import MenuItem, Category, Rating, Order, Cart, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, RatingSerializer, UserOrdersSerializer, \
    UserCartSerializer, UserSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .throttles import TenCallsPerMinute
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User, Group

# Create your views here.
# class CustomPagination(PageNumberPagination):
#     page_size = 10  # Number of items per page
#     page_size_query_param = 'page_size'  # Customize the query parameter name for page size
#     max_page_size = 100  # Maximum number of items per page


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'id': ['exact'],
        'price': ['exact', 'gte', 'lte']
                        }
    ordering_fields = ['price', 'stock']
    search_fields = ['title', 'inventory']
    ordering = ['price']
    # pagination_class = CustomPagination


class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class category_detail(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SecretView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]  # Apply TokenAuthentication
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, **kwargs):
        return Response({"message": "Some secret message"})


class ManagerView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]  # Apply TokenAuthentication
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            return Response({"message": "manage will see this"})
        else:
            return Response({"message": "You are not authorized"}, 403)


class NonUserView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, **kwargs):
        return Response({"message": "non user successful"})


class CustomerView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [TenCallsPerMinute]

    def throttle_customer_check(self, request, **kwargs):
        if request.user.groups.filter(name="").exists():
            return Response({"message": "logged user only"})
        else:
            return Response({"message": "not"})


class RatingsView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []

        return [IsAuthenticated()]


class ManagerUsersView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Get the 'manager' group
        manager_group = Group.objects.get(name='Manager')
        # Get the users in the 'manager' group
        queryset = User.objects.filter(groups=manager_group)
        return queryset

    def perform_create(self, serializer):
        # Assign the user to the 'manager' group
        manager_group = Group.objects.get(name='Manager')
        user = serializer.save()
        user.groups.add(manager_group)


class ManagerSingleUserView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Get the 'manager' group
        manager_group = Group.objects.get(name='Manager')
        # Get the users in the 'manager' group
        queryset = User.objects.filter(groups=manager_group)
        return queryset


class Delivery_crew_management(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        delivery_group = Group.objects.get(name='Delivery crew')
        queryset = User.objects.filter(groups=delivery_group)
        return queryset

    def perform_create(self, serializer):
        delivery_group = Group.objects.get(name='Delivery crew')
        user = serializer.save()
        user.groups.add(delivery_group)


class Delivery_crew_management_single_view(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        delivery_group = Group.objects.get(name='Delivery crew')
        queryset = User.objects.filter(groups=delivery_group)
        return queryset


class Customer_Cart(generics.ListCreateAPIView):
    serializer_class = UserCartSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def perform_create(self, serializer):
        menuitem = self.request.data.get('menuitem')
        quantity = self.request.data.get('quantity')
        unit_price = MenuItem.objects.get(pk=menuitem).price
        quantity = int(quantity)
        price = quantity * unit_price
        serializer.save(user=self.request.user, price=price)

    def delete(self, request):
        user = self.request.user
        Cart.objects.filter(user=user).delete()
        return Response(status=204)


class Orders_view(generics.ListCreateAPIView):
    serializer_class = UserOrdersSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    def perform_create(self, serializer):
        cart_items = Cart.objects.filter(user=self.request.user)
        total = self.calculate_total(cart_items)
        order = serializer.save(user=self.request.user, total=total)

        for cart_item in cart_items:
            OrderItem.objects.create(menuitem=cart_item.menuitem, quantity=cart_item.quantity,
                                     unit_price=cart_item.unit_price, price=cart_item.price, order=order)
            cart_item.delete()

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)


    def calculate_total(self, cart_items):
        total = Decimal(0)
        for item in cart_items:
            total += item.price
        return total


class Single_Order_view(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserOrdersSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)