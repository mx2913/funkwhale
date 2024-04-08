from django.conf.urls import include
from django.urls import re_path

from funkwhale_api.common import routers as common_routers

router = common_routers.OptionalSlashRouter()
v2_patterns = router.urls

v2_patterns += [
    re_path(
        r"^instance/",
        include(("funkwhale_api.instance.urls_v2", "instance"), namespace="instance"),
    ),
    re_path(
        r"^radios/",
        include(("funkwhale_api.radios.urls_v2", "radios"), namespace="radios"),
    ),
    # to do : to delete
    # re_path(
    #     r"^users/",
    #     include(("funkwhale_api.users.api_urls_v2", "users"), namespace="users"),
    # ),
]

urlpatterns = [re_path("", include((v2_patterns, "v2"), namespace="v2"))]
