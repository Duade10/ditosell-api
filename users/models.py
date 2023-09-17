from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


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
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(choices=USER_TYPES, max_length=10)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = str.capitalize(self.first_name)
        if self.last_name:
            self.last_name = str.capitalize(self.last_name)
        super().save(*args, **kwargs)
