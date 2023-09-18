from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Account Verification Imports
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email Field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    USER_TYPE_ADMIN = "admin"
    USER_TYPE_CUSTOMER = "customer"

    USER_TYPES = (
        (USER_TYPE_ADMIN, "Admin"),
        (USER_TYPE_CUSTOMER, "Customer"),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(choices=USER_TYPES, max_length=10)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if self.email:
            self.username = self.email.split("@")[0]
        if self.first_name:
            self.first_name = str.capitalize(self.first_name)
        if self.last_name:
            self.last_name = str.capitalize(self.last_name)
        super().save(*args, **kwargs)

    def verify_email(self, request):
        current_site = get_current_site(request)
        domain = current_site
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        token = default_token_generator.make_token(self)
        activate_url = f"http://{domain}/api/users/activate/{token}/{uid}"

        html_message = render_to_string("registration_email.html", {"activate_url": activate_url})

        send_mail(
            "Confirm Your Email Address for Access to Our Logistics Services",
            strip_tags(html_message),
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=False,
            html_message=html_message,
        )
        self.save()
