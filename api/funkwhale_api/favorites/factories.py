import factory
from django.utils import timezone

from funkwhale_api.factories import NoUpdateOnCreate, registry
from funkwhale_api.music.factories import TrackFactory
from funkwhale_api.users.factories import UserFactory


@registry.register
class TrackFavorite(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    track = factory.SubFactory(TrackFactory)
    user = factory.SubFactory(UserFactory)
    creation_date = factory.Faker("date_time_this_decade", tzinfo=timezone.utc)

    class Meta:
        model = "favorites.TrackFavorite"
