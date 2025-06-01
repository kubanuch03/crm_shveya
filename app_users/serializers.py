from rest_framework import serializers
from django.core.exceptions import ValidationError

from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta: 
        model = User
        fields = ['id','username','email','is_active','is_superuser']



class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username','password']


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False)
    username= serializers.CharField(required=True)
    password = serializers.CharField(required=True,write_only=True)
    password_confirm = serializers.CharField(required=True,write_only=True)


    class Meta: 
        model = User
        fields = ['id','username','email','is_active', 'password', 'password_confirm']


    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        
       
        return attrs
    

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        try:
            user = User.objects.create_user(**validated_data)
            user.is_active = True
            user.save()
            return user
        except:
            raise serializers.ValidationError({"dublicate":"user exists!"})