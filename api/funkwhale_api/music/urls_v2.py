from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()

router.register(r"artists", views.V2_ArtistsViewSet, "artists")


urlpatterns = router.urls
