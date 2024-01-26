from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse, FileResponse


from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from funkwhale_api.common import fields, permissions
from funkwhale_api.music import utils as music_utils
from funkwhale_api.music import models as music_models
from funkwhale_api.music import serializers as music_serializers


from funkwhale_api.users.oauth import permissions as oauth_permissions

from . import filters, models, serializers, utils, renderers, parsers


class PlaylistViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.PlaylistSerializer
    queryset = (
        models.Playlist.objects.all()
        .select_related("user__actor__attachment_icon")
        .annotate(tracks_count=Count("playlist_tracks", distinct=True))
        .with_covers()
        .with_duration()
    )
    permission_classes = [
        oauth_permissions.ScopePermission,
        permissions.OwnerPermission,
    ]
    required_scope = "playlists"
    anonymous_policy = "setting"
    owner_checks = ["write"]
    filterset_class = filters.PlaylistFilter
    ordering_fields = ("id", "name", "creation_date", "modification_date")
    parser_classes = [parsers.XspfParser, JSONParser, FormParser, MultiPartParser]

    # https://docs.djangoproject.com/en/5.0/topics/class-based-views/generic-editing/#content-negotiation-example
    # https://docs.djangoproject.com/en/5.0/ref/request-response/#django.http.HttpRequest.__iter__

    def create(self, request, *args, **kwargs):
        content_type = request.headers.get("Content-Type")
        if content_type and "application/octet-stream" in request.headers.get(
            "Content-Type"
        ):
            tracks, plt_name = utils.get_tracks_from_xspf(request.data)
            plt = models.Playlist.objects.create(
                name=plt_name, privacy_level="private", user=self.request.user
            )
            plt.insert_many(tracks)
            plt = serializers.PlaylistSerializer(plt)
            return Response(plt.data, status=201)
        response = super().create(request, *args, **kwargs)
        return response

    def retrieve(self, request, pk, *args, **kwargs):
        content_type = request.headers.get("Content-Type")
        if content_type and "application/octet-stream" in request.headers.get(
            "Content-Type"
        ):
            playlist = self.get_object()
            xspf = utils.generate_xspf_from_playlist(pk)
            # https://docs.djangoproject.com/en/5.0/ref/request-response/#telling-the-browser-to-treat-the-response-as-a-file-attachment
            # shoud we use https://docs.djangoproject.com/en/5.0/ref/request-response/#fileresponse-objects ?
            # eg FileResponse(xspf, as_attachment=True, filename=f"{playlist.name}.xspf")
            response = HttpResponse(
                xspf,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Content-Disposition": f'attachment; filename="{playlist.name}.xspf"',
                },
            )
            return response

        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        playlist = self.get_object()
        content_type = request.headers.get("Content-Type")
        if content_type and "application/octet-stream" in request.headers.get(
            "Content-Type"
        ):
            tracks, plt_name = utils.get_tracks_from_xspf(request.data)
            playlist.playlist_tracks.all().delete()
            playlist.insert_many(tracks)
            models.Playlist.objects.filter(pk=self.kwargs["pk"]).update(
                name=plt_name,
                user_id=playlist.user.id,
                privacy_level=playlist.privacy_level,
            )
            playlist.refresh_from_db()
            serializer = serializers.PlaylistSerializer(playlist)
            return Response(serializer.data, status=201)

        else:
            return super().retrieve(request, *args, **kwargs)

    @extend_schema(responses=serializers.PlaylistTrackSerializer(many=True))
    @action(methods=["get"], detail=True)
    def tracks(self, request, *args, **kwargs):
        playlist = self.get_object()
        plts = playlist.playlist_tracks.all().for_nested_serialization(
            music_utils.get_actor_from_request(request)
        )
        serializer = serializers.PlaylistTrackSerializer(plts, many=True)
        data = {"count": len(plts), "results": serializer.data}
        return Response(data, status=200)

    @extend_schema(
        operation_id="add_to_playlist", request=serializers.PlaylistAddManySerializer
    )
    @action(methods=["post"], detail=True)
    @transaction.atomic
    def add(self, request, *args, **kwargs):
        playlist = self.get_object()
        serializer = serializers.PlaylistAddManySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            plts = playlist.insert_many(
                serializer.validated_data["tracks"],
                serializer.validated_data["allow_duplicates"],
            )
        except exceptions.ValidationError as e:
            payload = {"playlist": e.detail}
            return Response(payload, status=400)
        ids = [p.id for p in plts]
        plts = (
            models.PlaylistTrack.objects.filter(pk__in=ids)
            .order_by("index")
            .for_nested_serialization(music_utils.get_actor_from_request(request))
        )
        serializer = serializers.PlaylistTrackSerializer(plts, many=True)
        data = {"count": len(plts), "results": serializer.data}
        return Response(data, status=201)

    @extend_schema(operation_id="clear_playlist")
    @action(methods=["delete"], detail=True)
    @transaction.atomic
    def clear(self, request, *args, **kwargs):
        playlist = self.get_object()
        playlist.playlist_tracks.all().delete()
        playlist.save(update_fields=["modification_date"])
        return Response(status=204)

    def get_queryset(self):
        return self.queryset.filter(
            fields.privacy_level_query(self.request.user)
        ).with_playable_plts(music_utils.get_actor_from_request(self.request))

    def perform_create(self, serializer):
        return serializer.save(
            user=self.request.user,
            privacy_level=serializer.validated_data.get(
                "privacy_level", self.request.user.privacy_level
            ),
        )

    @extend_schema(operation_id="remove_from_playlist")
    @action(methods=["post", "delete"], detail=True)
    @transaction.atomic
    def remove(self, request, *args, **kwargs):
        playlist = self.get_object()
        try:
            index = int(request.data["index"])
            assert index >= 0
        except (KeyError, ValueError, AssertionError, TypeError):
            return Response(status=400)

        try:
            plt = playlist.playlist_tracks.by_index(index)
        except models.PlaylistTrack.DoesNotExist:
            return Response(status=404)
        plt.delete(update_indexes=True)

        return Response(status=204)

    @extend_schema(operation_id="reorder_track_in_playlist")
    @action(methods=["post"], detail=True)
    @transaction.atomic
    def move(self, request, *args, **kwargs):
        playlist = self.get_object()
        try:
            from_index = int(request.data["from"])
            assert from_index >= 0
        except (KeyError, ValueError, AssertionError, TypeError):
            return Response({"detail": "invalid from index"}, status=400)

        try:
            to_index = int(request.data["to"])
            assert to_index >= 0
        except (KeyError, ValueError, AssertionError, TypeError):
            return Response({"detail": "invalid to index"}, status=400)

        try:
            plt = playlist.playlist_tracks.by_index(from_index)
        except models.PlaylistTrack.DoesNotExist:
            return Response(status=404)
        playlist.insert(plt, to_index)
        return Response(status=204)

    @extend_schema(operation_id="get_playlist_releases")
    @action(methods=["get"], detail=True)
    @transaction.atomic
    def releases(self, request, *args, **kwargs):
        playlist = self.get_object()
        try:
            releases_pks = playlist.playlist_tracks.values_list(
                "track__album__pk", flat=True
            ).distinct()
        except models.PlaylistTrack.DoesNotExist:
            return Response(status=404)
        releases = music_models.Album.objects.filter(pk__in=releases_pks)
        serializer = music_serializers.AlbumSerializer(data=releases, many=True)
        serializer.is_valid()
        return Response(serializer.data, status=200)

    @extend_schema(operation_id="get_playlist_artits")
    @action(methods=["get"], detail=True)
    @transaction.atomic
    def artists(self, request, *args, **kwargs):
        playlist = self.get_object()
        try:
            artists_pks = playlist.playlist_tracks.values_list(
                "track__artist__pk", flat=True
            ).distinct()
        except models.PlaylistTrack.DoesNotExist:
            return Response(status=404)
        artists = music_models.Artist.objects.filter(pk__in=artists_pks)
        serializer = music_serializers.SimpleArtistSerializer(data=artists, many=True)
        serializer.is_valid()
        return Response(serializer.data, status=200)
