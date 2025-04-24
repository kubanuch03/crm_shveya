
from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

from config.custom_loggs.custom_log import setup_logger

from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer
from .models import User
from .forms import UserProfileForm

from .services.user_register import UserRegisterServices


logger = setup_logger(__name__)


def very_simple_user_menu_items(request):
    print("--- DEBUG: ВЫЗВАНА very_simple_user_menu_items ---")
    items = [
        {"title": "Профиль Меню 1", "link": "/admin/", "icon": "person"},
        {"title": "Выход Меню 2", "link": "/admin/logout/", "icon": "logout"},
    ]
    print(f"--- DEBUG: very_simple_user_menu_items ВОЗВРАЩАЕТ: {items} ---")
    return items

#======================================================
# User CRUD
#======================================================
class UserListView(views.APIView):

    def get(self,request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserDetailView(views.APIView):

    def get(self,request,id):
        
        try:
            queryset = User.objects.get(id=id)
        except :
            return Response({"error":"user does not exists"})
        serializer = UserSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

#======================================================
# User Authorization
#======================================================
class UserRegisterView(views.APIView):
    
    def post(self,request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info({'success':"user create"})
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(views.APIView):

    def post(self,request):
        serializer = TokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            tokens = serializer.validated_data
            return Response(tokens, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





#======================================================
# dashboard callback
#======================================================
