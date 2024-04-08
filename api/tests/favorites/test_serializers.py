from funkwhale_api.favorites import serializers
from funkwhale_api.federation import serializers as federation_serializers
from funkwhale_api.music import serializers as music_serializers


def test_track_favorite_serializer(factories, to_api_date):
    favorite = factories["favorites.TrackFavorite"]()

    expected = {
        "id": favorite.pk,
        "creation_date": to_api_date(favorite.creation_date),
        "track": music_serializers.TrackSerializer(favorite.track).data,
        "actor": federation_serializers.APIActorSerializer(favorite.actor).data,
    }
    serializer = serializers.UserTrackFavoriteSerializer(favorite)

    assert serializer.data == expected
