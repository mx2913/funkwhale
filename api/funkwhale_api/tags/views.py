import django_filters.rest_framework
from django.db.models.functions import Collate

from django.db.models import functions
from rest_framework import viewsets

from funkwhale_api.users.oauth import permissions as oauth_permissions

from . import filters, models, serializers


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "name"
    queryset = (
        models.Tag.objects.all()
        .annotate(__size=functions.Length("name"))
        .annotate(tag_deterministic=Collate("name", "und-x-icu"))
        .order_by("name")
    )
    serializer_class = serializers.TagSerializer
    permission_classes = [oauth_permissions.ScopePermission]
    required_scope = "libraries"
    anonymous_policy = "setting"
    filterset_class = filters.TagFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
