import uuid
from bson import ObjectId
import jwt

import bcrypt
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


from db_connection import db

users = db["Users"]


USER_TYPE_ADMIN = "admin"
USER_TYPE_CUSTOMER = "customer"

USER_TYPES = (
    (USER_TYPE_ADMIN, "Admin"),
    (USER_TYPE_CUSTOMER, "Customer"),
)

LOGIN_TYPE_EMAIL = "email"
LOGIN_TYPE_GOOGLE = "google"
LOGIN_TYPE_APPLE = "apple"

LOGIN_TYPES = (
    (LOGIN_TYPE_EMAIL, "Email"),
    (LOGIN_TYPE_GOOGLE, "Admin"),
    (LOGIN_TYPE_APPLE, "Apple"),
)


class User:
    """User Model Class"""

    def __init__(self, user_dict=None):
        self.users = db["users"]

        if user_dict:
            self.email = user_dict["email"]
            self.password = user_dict["password"]
            try:
                self.first_name = user_dict["first_name"]
                self.last_name = user_dict["last_name"]
            except KeyError:
                self.first_name = None
                self.last_name = None
            self.user_type = user_dict["user_type"]
            self.login_type = user_dict["login_type"]
            self.is_active = user_dict["is_active"]
        else:
            self.email = None
            self.password = None
            self.first_name = None
            self.last_name = None
            self.date_joined = None
            self.user_type = None
            self.login_type = None
            self.is_active = None

    def get_user(self, string_value=None, value=None):
        if string_value:
            query = {string_value: value}

        user = self.users.find_one(query)

        if user:
            return {
                "email": user["email"],
                "id": user["id"],
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "username": user.get("username"),
                "date_joined": user.get("date_joined"),
                "user_type": user.get("user_type"),
                "login_type": user.get("login_type"),
                "is_active": user.get("is_active"),
                "password": user.get("password"),
            }
        return None

    def add_user(self):
        """Takes User Dictionary As Input, Save User To DB And Returns User Object"""

        custom_id = str(uuid.uuid4())
        verification_token = str(uuid.uuid4())
        username = self.email.split("@")[0]

        new_user = {
            "id": custom_id,
            "email": self.email,
            "username": username,
            "password": bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt()),
            "verification_token": verification_token,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_joined": str(timezone.now()),
            "user_type": self.user_type,
            "login_type": self.login_type,
            "is_active": self.is_active,
            "last_login": None,
        }

        self.users.insert_one(new_user).inserted_id
        new_user = self.get_user("email", self.email)
        return new_user

    def update_last_login(self, user_id):
        """Update the last_login field when a user logs in"""

        now = str(timezone.now())
        self.users.update_one({"id": user_id}, {"$set": {"last_login": now}})

    def update_user(self, user_id, user_dict):
        self.users.update_one({"id": user_id}, {"$set": user_dict})
        user = self.get_user("id", user_id)
        return user

    def verify_email(self, request):
        user = self.get_user_by_email(self.email)
        current_site = get_current_site(request)
        domain = current_site.domain
        token = user["verification_token"]
        activate_url = f"http://{domain}/api/users/activate/{token}"

        html_message = render_to_string("registration_email.html", {"activate_url": activate_url})

        send_mail(
            "Confirm Your Email Address for Access to Our Logistics Services",
            strip_tags(html_message),
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=False,
            html_message=html_message,
        )

    def activate_user(self, uid, token):
        try:
            uid = force_text(urlsafe_base64_decode(uid))
            user = self.users.find_one({"_id": uid})
            if user and default_token_generator.check_token(user, token):
                user["is_active"] = True
                self.users.save(user)
                return True
            else:
                return False
        except Exception as e:
            return False


class MongoDBAuthentication(authentication.BaseAuthentication):
    """Checks User Password and returns user object"""

    def authenticate(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user_instance = User()

        user = user_instance.get_user("email", email)

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            return (user, None)
        else:
            raise AuthenticationFailed("Invalid credentials")
