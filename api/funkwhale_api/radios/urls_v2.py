from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()

router.register(r"tracks", views.RadioSessionTracksViewSet, "tracks")


urlpatterns = router.urls
