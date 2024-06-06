import uuid
from django.db import models
from django.utils import timezone
from django.urls import reverse

from funkwhale_api.common import fields
from funkwhale_api.common import models as common_models

from funkwhale_api.music.models import Track
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import utils as federation_utils

FAVORITE_PRIVACY_LEVEL_CHOICES = [
    (k, l) for k, l in fields.PRIVACY_LEVEL_CHOICES if k != "followers"
]


class TrackFavoriteQuerySet(models.QuerySet, common_models.LocalFromFidQuerySet):
    def viewable_by(self, actor):
        if actor is None:
            return self.filter(actor__privacy_level="everyone")

        if hasattr(actor, "user"):
            me_query = models.Q(actor__privacy_level="me", actor=actor)
        me_query = models.Q(actor__privacy_level="me", actor=actor)

        instance_query = models.Q(
            actor__privacy_level="instance", actor__domain=actor.domain
        )
        instance_actor_query = models.Q(
            actor__privacy_level="instance", actor__domain=actor.domain
        )

        return self.filter(
            me_query
            | instance_query
            | instance_actor_query
            | models.Q(actor__privacy_level="everyone")
        )


class TrackFavorite(federation_models.FederationMixin):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    creation_date = models.DateTimeField(default=timezone.now)
    actor = models.ForeignKey(
        "federation.Actor",
        related_name="track_favorites",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    track = models.ForeignKey(
        Track, related_name="track_favorites", on_delete=models.CASCADE
    )
    source = models.CharField(max_length=100, null=True, blank=True)

    federation_namespace = "likes"
    objects = TrackFavoriteQuerySet.as_manager()

    class Meta:
        unique_together = ("track", "actor")

        ordering = ("-creation_date",)

    @classmethod
    def add(cls, track, actor):
        favorite, created = cls.objects.get_or_create(actor=actor, track=track)
        return favorite

    def get_activity_url(self):
        return f"{self.actor.get_absolute_url()}/favorites/tracks/{self.pk}"

    def get_federation_id(self):
        if self.fid:
            return self.fid

        return federation_utils.full_url(
            reverse(
                f"federation:music:{self.federation_namespace}-detail",
                kwargs={"uuid": self.uuid},
            )
        )

    def save(self, **kwargs):
        if not self.pk and not self.fid:
            self.fid = self.get_federation_id()

        return super().save(**kwargs)
