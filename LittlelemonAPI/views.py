from django.shortcuts import render, get_object_or_404
from rest_framework import generics, filters, viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from .models import MenuItem, Category, Rating
from .serializers import MenuItemSerializer, CategorySerializer, RatingSerializer
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
    permission_classes = [IsAuthenticated, IsAdminUser]  # Ensure the user is authenticated

    def get(self, request, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            return Response({"message": "manage will see this"})
        else:
            return Response({"message": "You are not authorized"}, 403)


class ManagerAdminView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    lookup_field = 'username'

    def perform_action(self, action):
        username = self.request.data.get('username')
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")

            if action == 'add':
                managers.user_set.add(user)
            elif action == 'remove':
                managers.user_set.remove(user)

            return Response({"message": "0k"})

        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        return self.perform_action('add')

    def destroy(self, request, *args, **kwargs):
        return self.perform_action('remove')

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
        if(self.request.method=='GET'):
            return []

        return [IsAuthenticated()]