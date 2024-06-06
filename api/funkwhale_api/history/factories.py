import factory
from funkwhale_api.factories import NoUpdateOnCreate, registry
from funkwhale_api.music import factories
from funkwhale_api.federation.factories import ActorFactory


@registry.register
class ListeningFactory(NoUpdateOnCreate, factory.django.DjangoModelFactory):
    actor = factory.SubFactory(ActorFactory)
    track = factory.SubFactory(factories.TrackFactory)
    fid = factory.Faker("federation_url")
    uuid = factory.Faker("uuid4")

    class Meta:
        model = "history.Listening"
