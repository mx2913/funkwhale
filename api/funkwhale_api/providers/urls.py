from django.conf.urls import include
from django.urls import re_path

urlpatterns = [
    re_path(
        r"^musicbrainz/",
        include(
            ("funkwhale_api.musicbrainz.urls", "musicbrainz"), namespace="musicbrainz"
        ),
    )
]
