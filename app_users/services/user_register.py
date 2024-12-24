from config.custom_loggs.custom_log import setup_logger

from rest_framework.response import Response


from ..models import User
from ..serializers import UserRegisterSerializer

logger = setup_logger(__name__)

class UserRegisterServices:

    def __init__(self):
        pass