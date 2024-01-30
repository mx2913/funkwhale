from django.urls import re_path

from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()
router.register(r"users", views.UserViewSet, "users")

urlpatterns = [
    re_path(r"^users/login/?$", views.login, name="login"),
    re_path(r"^users/logout/?$", views.logout, name="logout"),
] + router.urls
