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
            uuid = payload.get("uuid")
            tokens = db["token"]
            token = tokens.find_one({"uuid": uuid})
            user = self.get_user_from_mongodb(token["user_id"])
            if user is None:
                raise AuthenticationFailed("User not found")
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
        user = users.find_one({"id": user_id})
        return user
