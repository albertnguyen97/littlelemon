from django.urls import path
from . import views
from rest_framework.authtoken.views import ObtainAuthToken, obtain_auth_token

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('category', views.CategoryView.as_view()),
    path('category/<int:pk>', views.category_detail.as_view(), name='category-detail'),
    path('secret', views.SecretView.as_view()),
    path('manager-view', views.ManagerView.as_view()),
    path('api-token-auth', obtain_auth_token),
    path('throttle-check', views.NonUserView.as_view()),
    path('throttle-check-auth', views.CustomerView.as_view()),
    path('groups/manager/users', views.ManagerAdminView.as_view()),
    path('ratings', views.RatingsView.as_view())
]