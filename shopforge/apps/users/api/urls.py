"""URL configuration for the Users API."""
from django.urls import path

from .views import UserProfileView

app_name = "users"

urlpatterns = [
    path("me/", UserProfileView.as_view(), name="profile"),
]