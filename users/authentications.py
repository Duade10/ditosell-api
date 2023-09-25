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


import jwt
from datetime import datetime, timedelta
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

            # Check if the token is valid and not expired
            if not self.is_token_valid(token):
                raise AuthenticationFailed("Token has expired")

            user = self.get_user_from_mongodb(token["user_id"])
            if user is None:
                raise AuthenticationFailed("User not found")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.DecodeError:
            raise AuthenticationFailed("Token is invalid")

        return (user, None)

    def is_token_valid(self, token):
        created_at = token.get("created_at")
        if created_at:
            # Convert the created_at string to a datetime object
            created_at_datetime = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")

            # Calculate the token expiration time (1 hour)
            token_expiration_time = created_at_datetime + timedelta(hours=1)

            # Check if the current time is before the token expiration time
            return datetime.utcnow() <= token_expiration_time

        return False

    def get_token_from_request(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if header.startswith("Bearer "):
            return header.split(" ")[1]
        return None

    def get_user_from_mongodb(self, user_id):
        users = db["users"]
        user = users.find_one({"id": user_id})
        return user


def generate_token(user_id) -> dict:
    tokens = db["token"]
    payload = {"uuid": str(uuid.uuid4()), "created_at": datetime.utcnow().isoformat()}
    key = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    old_token = tokens.find_one({"user_id": user_id})
    if old_token:
        tokens.update_one({"_id": old_token["_id"]}, {"$set": {"is_valid": False}})
    token = {"key": key, "uuid": payload["uuid"], "is_valid": True, "user_id": user_id}
    tokens.insert_one(token)
    return token
