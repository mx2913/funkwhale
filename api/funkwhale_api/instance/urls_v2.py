from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^nodeinfo/2.1/?$", views.NodeInfo21.as_view(), name="nodeinfo-2.1"),
]
