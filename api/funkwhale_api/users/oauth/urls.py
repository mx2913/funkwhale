from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt

from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()
router.register(r"apps", views.ApplicationViewSet, "apps")
router.register(r"grants", views.GrantViewSet, "grants")

urlpatterns = router.urls + [
    re_path(
        "^authorize/$", csrf_exempt(views.AuthorizeView.as_view()), name="authorize"
    ),
    re_path("^token/$", views.TokenView.as_view(), name="token"),
    re_path("^revoke/$", views.RevokeTokenView.as_view(), name="revoke"),
]
