from rest_framework import permissions
from .authentications import CustomTokenAuthentication


class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated using your custom authentication class
        user, auth = CustomTokenAuthentication().authenticate(request)

        # If the user is authenticated, allow access; otherwise, deny access
        return user is not None
