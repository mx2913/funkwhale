from funkwhale_api.common import routers

from . import views

router = routers.OptionalSlashRouter()

router.register(r"^", views.V2_list_artists, "artists")


urlpatterns = router.urls
