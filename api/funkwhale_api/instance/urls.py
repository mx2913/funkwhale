from django.urls import re_path

from funkwhale_api.common import routers

from . import views

admin_router = routers.OptionalSlashRouter()
admin_router.register(r"admin/settings", views.AdminSettings, "admin-settings")

urlpatterns = [
    re_path(r"^nodeinfo/2.0/?$", views.NodeInfo20.as_view(), name="nodeinfo-2.0"),
    re_path(r"^settings/?$", views.InstanceSettings.as_view(), name="settings"),
    re_path(r"^spa-manifest.json", views.SpaManifest.as_view(), name="spa-manifest"),
] + admin_router.urls
