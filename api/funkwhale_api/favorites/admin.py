from funkwhale_api.common import admin

from . import models


@admin.register(models.TrackFavorite)
class TrackFavoriteAdmin(admin.ModelAdmin):
    list_display = ["actor", "track", "creation_date"]
    list_select_related = ["actor", "track"]
