from rest_framework import mixins, response, viewsets
from rest_framework import decorators as rest_decorators
from django.shortcuts import get_object_or_404

from funkwhale_api.common import preferences, decorators
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import tasks as federation_tasks
from funkwhale_api.music import models as music_models
from funkwhale_api.moderation import models as moderation_models
from funkwhale_api.users import models as users_models


from . import filters, serializers


class ManageUploadViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = (
        music_models.Upload.objects.all()
        .select_related("track__artist", "track__album__artist")
        .order_by("-id")
    )
    serializer_class = serializers.ManageUploadSerializer
    filterset_class = filters.ManageUploadFilterSet
    required_scope = "instance:libraries"
    ordering_fields = [
        "accessed_date",
        "modification_date",
        "creation_date",
        "track__artist__name",
        "bitrate",
        "size",
        "duration",
    ]

    @rest_decorators.action(methods=["post"], detail=False)
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageUploadActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)


class ManageUserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = users_models.User.objects.all().order_by("-id")
    serializer_class = serializers.ManageUserSerializer
    filterset_class = filters.ManageUserFilterSet
    required_scope = "instance:users"
    ordering_fields = ["date_joined", "last_activity", "username"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["default_permissions"] = preferences.get("users__default_permissions")
        return context


class ManageInvitationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        users_models.Invitation.objects.all()
        .order_by("-id")
        .prefetch_related("users")
        .select_related("owner")
    )
    serializer_class = serializers.ManageInvitationSerializer
    filterset_class = filters.ManageInvitationFilterSet
    required_scope = "instance:invitations"
    ordering_fields = ["creation_date", "expiration_date"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @rest_decorators.action(methods=["post"], detail=False)
    def action(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ManageInvitationActionSerializer(
            request.data, queryset=queryset
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return response.Response(result, status=200)


class ManageDomainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_value_regex = r"[a-zA-Z0-9\-\.]+"
    queryset = (
        federation_models.Domain.objects.external()
        .with_actors_count()
        .with_outbox_activities_count()
        .prefetch_related("instance_policy")
        .order_by("name")
    )
    serializer_class = serializers.ManageDomainSerializer
    filterset_class = filters.ManageDomainFilterSet
    required_scope = "instance:domains"
    ordering_fields = [
        "name",
        "creation_date",
        "nodeinfo_fetch_date",
        "actors_count",
        "outbox_activities_count",
        "instance_policy",
    ]

    @rest_decorators.action(methods=["get"], detail=True)
    def nodeinfo(self, request, *args, **kwargs):
        domain = self.get_object()
        federation_tasks.update_domain_nodeinfo(domain_name=domain.name)
        domain.refresh_from_db()
        return response.Response(domain.nodeinfo, status=200)

    @rest_decorators.action(methods=["get"], detail=True)
    def stats(self, request, *args, **kwargs):
        domain = self.get_object()
        return response.Response(domain.get_stats(), status=200)

    action = decorators.action_route(serializers.ManageDomainActionSerializer)


class ManageActorViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    lookup_value_regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    queryset = (
        federation_models.Actor.objects.all()
        .with_uploads_count()
        .order_by("-creation_date")
        .select_related("user")
        .prefetch_related("instance_policy")
    )
    serializer_class = serializers.ManageActorSerializer
    filterset_class = filters.ManageActorFilterSet
    required_scope = "instance:accounts"
    required_permissions = ["moderation"]
    ordering_fields = [
        "name",
        "preferred_username",
        "domain",
        "fid",
        "creation_date",
        "last_fetch_date",
        "uploads_count",
        "outbox_activities_count",
        "instance_policy",
    ]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        username, domain = self.kwargs["pk"].split("@")
        filter_kwargs = {"domain_id": domain, "preferred_username": username}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)

        return obj

    @rest_decorators.action(methods=["get"], detail=True)
    def stats(self, request, *args, **kwargs):
        domain = self.get_object()
        return response.Response(domain.get_stats(), status=200)

    action = decorators.action_route(serializers.ManageActorActionSerializer)


class ManageInstancePolicyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        moderation_models.InstancePolicy.objects.all()
        .order_by("-creation_date")
        .select_related()
    )
    serializer_class = serializers.ManageInstancePolicySerializer
    filterset_class = filters.ManageInstancePolicyFilterSet
    required_scope = "instance:policies"
    ordering_fields = ["id", "creation_date"]

    def perform_create(self, serializer):
        serializer.save(actor=self.request.user.actor)
