from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserListView,UserDetailView, UserRegisterView, UserLoginView

app_name = 'users'
urlpatterns = [
    path('user/list/', UserListView.as_view(), name='user-list'),
    path('user/<int:id>/', UserDetailView.as_view(), name='user-register'),

    path('user/register/', UserRegisterView.as_view(), name='user-register'),
    path('user/login/', UserLoginView.as_view(), name='user-login'),


    # ==== Api Token =====
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Получение токена
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
]