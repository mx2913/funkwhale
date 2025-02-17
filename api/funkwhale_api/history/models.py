from django.db import models
from django.utils import timezone

from funkwhale_api.music.models import Track


class Listening(models.Model):
    creation_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    track = models.ForeignKey(
        Track, related_name="listenings", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "users.User",
        related_name="listenings",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    session_key = models.CharField(max_length=100, null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ("-creation_date",)

    def get_activity_url(self):
        return f"{self.user.get_activity_url()}/listenings/tracks/{self.pk}"
