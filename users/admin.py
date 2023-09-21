from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


# @admin.register(models.User)
# class CustomUserAdmin(UserAdmin):
#     list_display = (
#         "email",
#         "first_name",
#         "last_name",
#         "is_active",
#         "user_type",
#     )

#     fieldsets = UserAdmin.fieldsets + (
#         (
#             "Custom User Field(s)",
#             {
#                 "fields": ("user_type",),
#             },
#         ),
#     )
