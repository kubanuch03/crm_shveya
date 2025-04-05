
from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from config.custom_loggs.custom_log import setup_logger

from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer
from .models import User


from .services.user_register import UserRegisterServices


logger = setup_logger(__name__)



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
def dashboard_callback(request, context):
    total_users = User.objects.count()  
    latest_user = User.objects.latest('date_joined')  

    context.update({
        "total_users": total_users,
        "latest_user": latest_user,
    })
    return context