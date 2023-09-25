from django.urls import path

from . import views

app_name = "logistics"

urlpatterns = [
    path("", views.LogisticListView.as_view(), name="list"),
    path("create/", views.LogisticCreateView.as_view(), name="create"),
    path("detail/<str:id>/", views.LogisticDetailView.as_view(), name="detail"),
    path("rate/<str:logistic_id>/", views.LogisticRateListView.as_view(), name="list_rate"),
    path("rate/create/<str:logistic_id>/", views.LogisticRateCreateView.as_view(), name="create_rate"),
    path(
        "rate/detail/<str:logistic_id>/<str:logistic_rate_id>/",
        views.LogisticRateDetailView.as_view(),
        name="detail_rate",
    ),
]
