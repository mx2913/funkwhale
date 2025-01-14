from django.db import models
from django.utils import timezone

from funkwhale_api.music.models import Track


class TrackFavorite(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        "users.User", related_name="track_favorites", on_delete=models.CASCADE
    )
    track = models.ForeignKey(
        Track, related_name="track_favorites", on_delete=models.CASCADE
    )
    source = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ("track", "user")
        ordering = ("-creation_date",)

    @classmethod
    def add(cls, track, user):
        favorite, created = cls.objects.get_or_create(user=user, track=track)
        return favorite

    def get_activity_url(self):
        return f"{self.user.get_activity_url()}/favorites/tracks/{self.pk}"
