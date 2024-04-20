import uuid

from django.db import models
from django.utils import timezone
from django.urls import reverse
from funkwhale_api.common import models as common_models
from funkwhale_api.federation import models as federation_models
from funkwhale_api.federation import utils as federation_utils

from funkwhale_api.music.models import Track


class ListeningQuerySet(models.QuerySet, common_models.LocalFromFidQuerySet):
    pass


class Listening(federation_models.FederationMixin):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    creation_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    track = models.ForeignKey(
        Track, related_name="listenings", on_delete=models.CASCADE
    )
    # if actor is null it's a local TrackFavorite, maybe we should use `attributed_to` ?
    # Maybe we should use user instead : if user is null it's a remote object :
    # and delete the user attribute, but might be more work
    actor = models.ForeignKey(
        "federation.Actor",
        related_name="listenings",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    federation_namespace = "listenings"
    objects = ListeningQuerySet.as_manager()

    class Meta:
        ordering = ("-creation_date",)

    def get_activity_url(self):
        return f"{self.actor.get_absolute_url()}/listenings/tracks/{self.pk}"

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
