from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class APIKeyBackend(BaseBackend):
    def authenticate(self, request, api_key=None):
        from .models import APIKey
        try:
            api_key_obj = APIKey.objects.select_related('user').get(key=api_key, is_active=True)
            return api_key_obj.user
        except APIKey.DoesNotExist:
            return None