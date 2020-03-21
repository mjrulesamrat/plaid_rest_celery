from django.urls import path

from .views import ObtainAccessTokenView

urlpatterns = [
    path('create-item/', ObtainAccessTokenView.as_view(), name="create_item"),
]
