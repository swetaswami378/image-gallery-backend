from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path("auth/register", views.RegisterView.as_view(), name="register"),
    path("auth/login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("images/upload", views.ImageListCreateView.as_view(), name="image_list_create"),
    path("images/<int:pk>/", views.ImageRetrieveUpdateDeleteView.as_view(), name="image_rud"),
    path("images/<int:pk>/caption/", views.generate_caption_view, name="generate_caption"),
    path("images/", views.MyImagesListView.as_view(), name="my_images"),
]
