import factory

from funkwhale_api.factories import NoUpdateOnCreate, registry
from funkwhale_api.music.factories import TrackFactory
from funkwhale_api.users.factories import UserFactory
from funkwhale_api.federation.factories import ActorFactory
from funkwhale_api.federation import models

from django.conf import settings


@registry.register
class TrackFavorite(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    track = factory.SubFactory(TrackFactory)
    actor = factory.SubFactory(ActorFactory)
    fid = factory.Faker("federation_url")
    uuid = factory.Faker("uuid4")

    class Meta:
        model = "favorites.TrackFavorite"

    @factory.post_generation
    def local(self, create, extracted, **kwargs):
        if not extracted and not kwargs:
            return
        domain = models.Domain.objects.get_or_create(name=settings.FEDERATION_HOSTNAME)[
            0
        ]
        self.fid = f"https://{domain}/federation/music/favorite/{self.uuid}"
        self.save(update_fields=["domain", "fid"])
