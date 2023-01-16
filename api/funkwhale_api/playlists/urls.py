from django.conf.urls import url

from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()
router.register(r"playlists", views.PlaylistViewSet, "playlists")
router.register(r"import", views.PlaylistImportViewSet, "import")

urlpatterns = router.urls
