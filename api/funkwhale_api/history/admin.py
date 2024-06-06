from funkwhale_api.common import admin

from . import models


@admin.register(models.Listening)
class ListeningAdmin(admin.ModelAdmin):
    list_display = ["track", "creation_date", "actor", "session_key"]
    search_fields = ["track__name", "actor__user__username"]
    list_select_related = ["actor", "track"]
