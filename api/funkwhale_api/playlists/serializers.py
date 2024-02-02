from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.music.models import Album, Artist, Track

from funkwhale_api.music.serializers import TrackSerializer
from funkwhale_api.users.serializers import UserBasicSerializer
from . import models

import logging

logger = logging.getLogger(__name__)


class PlaylistTrackSerializer(serializers.ModelSerializer):
    # track = TrackSerializer()
    track = serializers.SerializerMethodField()

    class Meta:
        model = models.PlaylistTrack
        fields = ("track", "index", "creation_date")

    def get_track(self, o):
        track = o._prefetched_track if hasattr(o, "_prefetched_track") else o.track
        return TrackSerializer(track).data


class PlaylistSerializer(serializers.ModelSerializer):
    tracks_count = serializers.SerializerMethodField(read_only=True)
    duration = serializers.SerializerMethodField(read_only=True)
    album_covers = serializers.SerializerMethodField(read_only=True)
    user = UserBasicSerializer(read_only=True)
    is_playable = serializers.SerializerMethodField()
    actor = serializers.SerializerMethodField()

    class Meta:
        model = models.Playlist
        fields = (
            "id",
            "name",
            "user",
            "modification_date",
            "creation_date",
            "privacy_level",
            "tracks_count",
            "album_covers",
            "duration",
            "is_playable",
            "actor",
        )
        read_only_fields = ["id", "modification_date", "creation_date"]

    @extend_schema_field(federation_serializers.APIActorSerializer)
    def get_actor(self, obj):
        actor = obj.user.actor
        if actor:
            return federation_serializers.APIActorSerializer(actor).data

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_playable(self, obj):
        try:
            return bool(obj.playable_plts)
        except AttributeError:
            return None

    def get_tracks_count(self, obj) -> int:
        try:
            return obj.tracks_count
        except AttributeError:
            # no annotation?
            return obj.playlist_tracks.count()

    def get_duration(self, obj) -> int:
        try:
            return obj.duration
        except AttributeError:
            # no annotation?
            return 0

    @extend_schema_field({"type": "array", "items": {"type": "string"}})
    def get_album_covers(self, obj):
        try:
            plts = obj.plts_for_cover
        except AttributeError:
            return []

        excluded_artists = []
        try:
            user = self.context["request"].user
        except (KeyError, AttributeError):
            user = None
        if user and user.is_authenticated:
            excluded_artists = list(
                user.content_filters.values_list("target_artist", flat=True)
            )

        covers = []
        max_covers = 5
        for plt in plts:
            if plt.track.album.artist_id in excluded_artists:
                continue
            url = plt.track.album.attachment_cover.download_url_medium_square_crop
            if url in covers:
                continue
            covers.append(url)
            if len(covers) >= max_covers:
                break

        full_urls = []
        for url in covers:
            if "request" in self.context:
                url = self.context["request"].build_absolute_uri(url)
            full_urls.append(url)
        return full_urls


class PlaylistAddManySerializer(serializers.Serializer):
    tracks = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Track.objects.for_nested_serialization()
    )
    allow_duplicates = serializers.BooleanField(required=False)

    class Meta:
        fields = "allow_duplicates"


class XspfTrackSerializer(serializers.Serializer):
    location = serializers.CharField(allow_blank=True, required=False)
    title = serializers.CharField()
    creator = serializers.CharField()
    album = serializers.CharField(allow_blank=True, required=False)
    duration = serializers.CharField(allow_blank=True, required=False)

    def validate(self, data):
        artist = data["creator"]
        title = data["title"]
        album = data.get("album", None)
        try:
            artist_id = Artist.objects.get(name=artist)
        except ObjectDoesNotExist:
            raise ValidationError("Couldn't find artist in the database")
        if album:
            try:
                album_id = Album.objects.get(title=album)
                fw_track = Track.objects.get(
                    title=title, artist=artist_id.id, album=album_id
                )
            except ObjectDoesNotExist:
                pass
        try:
            fw_track = Track.objects.get(title=title, artist=artist_id.id)
        except ObjectDoesNotExist as e:
            raise ValidationError(f"Couldn't find track in the database : {e!r}")

        return fw_track


class XspfSerializer(serializers.Serializer):
    title = serializers.CharField()
    creator = serializers.CharField(allow_blank=True, required=False)
    creation_date = serializers.DateTimeField(required=False)
    version = serializers.IntegerField(required=False)
    tracks = XspfTrackSerializer(many=True, required=False)

    def create(self, validated_data):
        pl = models.Playlist.objects.create(
            name=validated_data["title"],
            privacy_level="private",
            user=validated_data["request"].user,
        )
        pl.insert_many(validated_data["tracks"])

        return pl

    def update(self, instance, validated_data):
        instance.name = validated_data["title"]
        instance.save()
        return instance
