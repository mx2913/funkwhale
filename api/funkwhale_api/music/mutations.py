from funkwhale_api.common import models as common_models
from funkwhale_api.common import mutations
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.common import utils as common_utils

from funkwhale_api.federation import routes
from funkwhale_api.tags import models as tags_models
from funkwhale_api.tags import serializers as tags_serializers

from . import models


def can_suggest(obj, actor):
    return obj.is_local


def can_approve(obj, actor):
    if not obj.is_local or not actor.user:
        return False

    return (
        actor.id is not None and actor.id == obj.attributed_to_id
    ) or actor.user.get_permissions()["library"]


class TagMutation(mutations.UpdateMutationSerializer):
    tags = tags_serializers.TagsListField()

    def get_previous_state_handlers(self):
        handlers = super().get_previous_state_handlers()
        handlers["tags"] = lambda obj: list(
            sorted(obj.tagged_items.values_list("tag__name", flat=True))
        )
        return handlers

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", [])
        r = super().update(instance, validated_data)
        tags_models.set_tags(instance, *tags)
        return r


class DescriptionMutation(mutations.UpdateMutationSerializer):
    description = common_serializers.ContentSerializer()

    def get_previous_state_handlers(self):
        handlers = super().get_previous_state_handlers()
        handlers["description"] = (
            lambda obj: common_serializers.ContentSerializer(obj.description).data
            if obj.description_id
            else None
        )
        return handlers

    def update(self, instance, validated_data):
        description = validated_data.pop("description", None)
        r = super().update(instance, validated_data)
        common_utils.attach_content(instance, "description", description)
        return r


@mutations.registry.connect(
    "update",
    models.Track,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class TrackMutationSerializer(TagMutation, DescriptionMutation):
    serialized_relations = {"license": "code"}

    class Meta:
        model = models.Track
        fields = ["license", "title", "position", "copyright", "tags", "description"]

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Track"}}, context={"track": obj}
        )


@mutations.registry.connect(
    "update",
    models.Artist,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class ArtistMutationSerializer(TagMutation, DescriptionMutation):
    class Meta:
        model = models.Artist
        fields = ["name", "tags", "description"]

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Artist"}}, context={"artist": obj}
        )


@mutations.registry.connect(
    "update",
    models.Album,
    perm_checkers={"suggest": can_suggest, "approve": can_approve},
)
class AlbumMutationSerializer(TagMutation, DescriptionMutation):
    cover = common_serializers.RelatedField(
        "uuid", queryset=common_models.Attachment.objects.all().local(), serializer=None
    )

    serialized_relations = {"cover": "uuid"}

    class Meta:
        model = models.Album
        fields = ["title", "release_date", "tags", "cover", "description"]

    def get_previous_state_handlers(self):
        handlers = super().get_previous_state_handlers()
        handlers["cover"] = (
            lambda obj: str(obj.attachment_cover.uuid) if obj.attachment_cover else None
        )
        return handlers

    def post_apply(self, obj, validated_data):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Album"}}, context={"album": obj}
        )

    def update(self, instance, validated_data):
        if "cover" in validated_data:
            validated_data["attachment_cover"] = validated_data.pop("cover")
        return super().update(instance, validated_data)

    def mutation_post_init(self, mutation):
        # link cover_attachment (if any) to mutation
        if "cover" not in mutation.payload:
            return
        try:
            attachment = common_models.Attachment.objects.get(
                uuid=mutation.payload["cover"]
            )
        except common_models.Attachment.DoesNotExist:
            return

        common_models.MutationAttachment.objects.create(
            attachment=attachment, mutation=mutation
        )
