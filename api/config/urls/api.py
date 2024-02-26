from django.conf.urls import include
from django.urls import re_path

from funkwhale_api.activity import views as activity_views
from funkwhale_api.audio import views as audio_views
from funkwhale_api.common import routers as common_routers
from funkwhale_api.common import views as common_views
from funkwhale_api.music import views
from funkwhale_api.playlists import views as playlists_views
from funkwhale_api.tags import views as tags_views

router = common_routers.OptionalSlashRouter()
router.register(r"activity", activity_views.ActivityViewSet, "activity")
router.register(r"tags", tags_views.TagViewSet, "tags")
router.register(r"plugins", common_views.PluginViewSet, "plugins")
router.register(r"tracks", views.TrackViewSet, "tracks")
router.register(r"uploads", views.UploadViewSet, "uploads")
router.register(r"libraries", views.LibraryViewSet, "libraries")
router.register(r"listen", views.ListenViewSet, "listen")
router.register(r"stream", views.StreamViewSet, "stream")
router.register(r"artists", views.ArtistViewSet, "artists")
router.register(r"channels", audio_views.ChannelViewSet, "channels")
router.register(r"subscriptions", audio_views.SubscriptionsViewSet, "subscriptions")
router.register(r"albums", views.AlbumViewSet, "albums")
router.register(r"licenses", views.LicenseViewSet, "licenses")
router.register(r"playlists", playlists_views.PlaylistViewSet, "playlists")
router.register(r"mutations", common_views.MutationViewSet, "mutations")
router.register(r"attachments", common_views.AttachmentViewSet, "attachments")
v1_patterns = router.urls

v1_patterns += [
    re_path(r"^oembed/$", views.OembedView.as_view(), name="oembed"),
    re_path(
        r"^instance/",
        include(("funkwhale_api.instance.urls", "instance"), namespace="instance"),
    ),
    re_path(
        r"^manage/",
        include(("funkwhale_api.manage.urls", "manage"), namespace="manage"),
    ),
    re_path(
        r"^moderation/",
        include(
            ("funkwhale_api.moderation.urls", "moderation"), namespace="moderation"
        ),
    ),
    re_path(
        r"^federation/",
        include(
            ("funkwhale_api.federation.api_urls", "federation"), namespace="federation"
        ),
    ),
    re_path(
        r"^providers/",
        include(("funkwhale_api.providers.urls", "providers"), namespace="providers"),
    ),
    re_path(
        r"^favorites/",
        include(("funkwhale_api.favorites.urls", "favorites"), namespace="favorites"),
    ),
    re_path(r"^search$", views.Search.as_view(), name="search"),
    re_path(
        r"^radios/",
        include(("funkwhale_api.radios.urls", "radios"), namespace="radios"),
    ),
    re_path(
        r"^history/",
        include(("funkwhale_api.history.urls", "history"), namespace="history"),
    ),
    re_path(
        r"^",
        include(("funkwhale_api.users.api_urls", "users"), namespace="users"),
    ),
    # XXX: remove if Funkwhale 1.1
    re_path(
        r"^users/",
        include(("funkwhale_api.users.api_urls", "users"), namespace="users-nested"),
    ),
    re_path(
        r"^oauth/",
        include(("funkwhale_api.users.oauth.urls", "oauth"), namespace="oauth"),
    ),
    re_path(r"^rate-limit/?$", common_views.RateLimitView.as_view(), name="rate-limit"),
    re_path(
        r"^text-preview/?$", common_views.TextPreviewView.as_view(), name="text-preview"
    ),
]

urlpatterns = [re_path("", include((v1_patterns, "v1"), namespace="v1"))]
