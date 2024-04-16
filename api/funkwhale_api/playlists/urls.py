from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()
router.register(r"playlists", views.PlaylistViewSet, "playlists")

urlpatterns = router.urls
