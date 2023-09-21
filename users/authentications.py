import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


from db_connection import db


class CustomTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = self.get_token_from_request(request)

        if token is None:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("uuid")
            user = self.get_user_from_mongodb(user_id)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.DecodeError:
            raise AuthenticationFailed("Token is invalid")

        return (user, None)

    def get_token_from_request(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if header.startswith("Bearer "):
            return header.split(" ")[1]
        return None

    def get_user_from_mongodb(self, user_id):
        users = db["users"]
        user = users.find_one({"uuid": user_id})
        return user
