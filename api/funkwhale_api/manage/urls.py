from django.conf.urls import include, url
from rest_framework import routers

from . import views

federation_router = routers.SimpleRouter()
federation_router.register(r"domains", views.ManageDomainViewSet, "domains")
library_router = routers.SimpleRouter()
library_router.register(r"uploads", views.ManageUploadViewSet, "uploads")
users_router = routers.SimpleRouter()
users_router.register(r"users", views.ManageUserViewSet, "users")
users_router.register(r"invitations", views.ManageInvitationViewSet, "invitations")

urlpatterns = [
    url(
        r"^federation/",
        include((federation_router.urls, "federation"), namespace="federation"),
    ),
    url(r"^library/", include((library_router.urls, "instance"), namespace="library")),
    url(r"^users/", include((users_router.urls, "instance"), namespace="users")),
]
