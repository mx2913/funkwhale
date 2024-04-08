from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from funkwhale_api.activity import serializers as activity_serializers
from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.music.serializers import TrackActivitySerializer, TrackSerializer
from funkwhale_api.users.serializers import UserActivitySerializer, UserBasicSerializer

from . import models


class ListeningActivitySerializer(activity_serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    object = TrackActivitySerializer(source="track")
    actor = federation_serializers.APIActorSerializer()
    published = serializers.DateTimeField(source="creation_date")

    class Meta:
        model = models.Listening
        fields = ["id", "local_id", "object", "type", "actor", "published"]

    def get_type(self, obj):
        return "Listen"


class ListeningSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    actor = federation_serializers.APIActorSerializer(read_only=True)

    class Meta:
        model = models.Listening
        fields = ("id", "actor", "track", "creation_date", "actor")

    def create(self, validated_data):
        validated_data["actor"] = self.context["user"].actor

        return super().create(validated_data)


class ListeningWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Listening
        fields = ("id", "actor", "track", "creation_date")

    def create(self, validated_data):
        validated_data["actor"] = self.context["user"].actor

        return super().create(validated_data)
