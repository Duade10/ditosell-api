from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls", namespace="users")),
    path("api/senders/", include("senders.urls", namespace="senders")),
    path("api/receivers/", include("receivers.urls", namespace="receivers")),
    path("api/shipments/", include("shipments.urls", namespace="shipments")),
]
