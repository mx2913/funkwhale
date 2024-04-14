from django.urls import re_path

from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()
router.register(r"search", views.SearchViewSet, "search")
urlpatterns = [
    re_path(
        "releases/(?P<uuid>[0-9a-z-]+)/$",
        views.ReleaseDetail.as_view(),
        name="release-detail",
    ),
    re_path(
        "artists/(?P<uuid>[0-9a-z-]+)/$",
        views.ArtistDetail.as_view(),
        name="artist-detail",
    ),
    re_path(
        "release-groups/browse/(?P<artist_uuid>[0-9a-z-]+)/$",
        views.ReleaseGroupBrowse.as_view(),
        name="release-group-browse",
    ),
    re_path(
        "releases/browse/(?P<release_group_uuid>[0-9a-z-]+)/$",
        views.ReleaseBrowse.as_view(),
        name="release-browse",
    ),
    # url('release-groups/(?P<uuid>[0-9a-z-]+)/$',
    #     views.ReleaseGroupDetail.as_view(),
    #     name='release-group-detail'),
] + router.urls
