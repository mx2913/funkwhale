# to do : to delete
# from django.urls import re_path, include

# from funkwhale_api.common import routers

# from funkwhale_api.federation import api_views as federation_views

# from . import views_v2


# router = routers.OptionalSlashRouter()
# router.register(r"", views_v2.UserViewSet, "users")

# urlpatterns = [
#     re_path(r"^login/?$", views_v2.login, name="login"),
#     re_path(r"^logout/?$", views_v2.logout, name="logout"),
#     re_path(
#         r"^(?P<user_pk>[0-9]+)/follow_requests/(?P<follow_pk>[0-9]+)/?$",
#         views_v2.follow_request_patch,
#         name="follow_request_patch",
#     ),
# ] + router.urls
