import pytest
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, QuerySet

from funkwhale_api.common import fields
from funkwhale_api.users.factories import UserFactory

from funkwhale_api.history import models
from funkwhale_api.favorites import models as favorite_models
from funkwhale_api.federation import models as federation_models


def test_privacy_level_query(factories):
    user = factories["users.User"](with_actor=True)
    user_query = (
        Q(privacy_level__in=["instance", "everyone"])
        | Q(privacy_level="me", user=user)
        | Q(
            privacy_level="followers",
            user__actor__pk__in=user.actor.user_follows.filter(
                approved=True
            ).values_list("target", flat=True),
        )
    )

    query = fields.privacy_level_query(user)
    assert str(query) == str(user_query)

    user = AnonymousUser()
    user_query = Q(privacy_level="everyone")
    query = fields.privacy_level_query(user)
    assert str(query) == str(user_query)


def test_privacy_level_query_followers(factories):
    user = factories["users.User"](with_actor=True)
    target = factories["users.User"]()
    target.create_actor(privacy_level="followers")

    target.refresh_from_db()

    userfollow = factories["federation.UserFollow"](
        actor=user.actor, target=target.actor, approved=True
    )
    listening = factories["history.Listening"](actor=userfollow.target)
    favorite = factories["favorites.TrackFavorite"](actor=userfollow.target)

    factories["history.Listening"]()
    factories["history.Listening"]()
    factories["favorites.TrackFavorite"]()
    factories["favorites.TrackFavorite"]()

    queryset = models.Listening.objects.all().filter(
        fields.privacy_level_query(user, "actor__privacy_level", "actor__user")
    )
    fav_qs = favorite_models.TrackFavorite.objects.all().filter(
        fields.privacy_level_query(user, "actor__privacy_level", "actor__user")
    )

    assert listening in queryset
    assert favorite in fav_qs


def test_privacy_level_query_not_followers(factories):
    user = factories["users.User"](with_actor=True)
    target = factories["users.User"]()
    target.create_actor(privacy_level="followers")

    target.refresh_from_db()

    userfollow = factories["federation.UserFollow"](target=target.actor, approved=True)
    listening = factories["history.Listening"](actor=userfollow.target)
    favorite = factories["favorites.TrackFavorite"](actor=userfollow.target)

    factories["history.Listening"]()
    factories["history.Listening"]()
    factories["favorites.TrackFavorite"]()
    factories["favorites.TrackFavorite"]()

    queryset = models.Listening.objects.all().filter(
        fields.privacy_level_query(user, "actor__privacy_level", "actor__user")
    )
    fav_qs = favorite_models.TrackFavorite.objects.all().filter(
        fields.privacy_level_query(user, "actor__privacy_level", "actor__user")
    )

    assert listening not in queryset
    assert favorite not in fav_qs


def test_generic_relation_field(factories):
    obj = factories["users.User"]()
    f = fields.GenericRelation(
        {
            "user": {
                "queryset": obj.__class__.objects.all(),
                "id_attr": "username",
                "id_field": fields.serializers.CharField(),
            }
        }
    )

    data = {"type": "user", "username": obj.username}

    assert f.to_internal_value(data) == obj


@pytest.mark.parametrize(
    "payload, expected_error",
    [
        ({}, r".*Invalid data.*"),
        (1, r".*Invalid data.*"),
        (False, r".*Invalid data.*"),
        ("test", r".*Invalid data.*"),
        ({"missing": "type"}, r".*Invalid type.*"),
        ({"type": "noop"}, r".*Invalid type.*"),
        ({"type": "user"}, r".*Invalid username.*"),
        ({"type": "user", "username": {}}, r".*Invalid username.*"),
        ({"type": "user", "username": "not_found"}, r".*Object not found.*"),
    ],
)
def test_generic_relation_field_validation_error(payload, expected_error, factories):
    obj = factories["users.User"]()
    f = fields.GenericRelation(
        {
            "user": {
                "queryset": obj.__class__.objects.all(),
                "id_attr": "username",
                "id_field": fields.serializers.CharField(),
            }
        }
    )

    with pytest.raises(fields.serializers.ValidationError, match=expected_error):
        f.to_internal_value(payload)


def test_generic_relation_filter_target_type(factories):
    user = factories["users.User"]()
    note = factories["moderation.Note"](target=user)
    factories["moderation.Note"](target=factories["music.Artist"]())
    f = fields.GenericRelationFilter(
        "target",
        {
            "user": {
                "queryset": user.__class__.objects.all(),
                "id_attr": "username",
                "id_field": fields.serializers.CharField(),
            }
        },
    )
    qs = f.filter(note.__class__.objects.all(), "user")
    assert list(qs) == [note]


def test_generic_relation_filter_target_type_and_id(factories):
    user = factories["users.User"]()
    note = factories["moderation.Note"](target=user)
    factories["moderation.Note"](target=factories["users.User"]())
    f = fields.GenericRelationFilter(
        "target",
        {
            "user": {
                "queryset": user.__class__.objects.all(),
                "id_attr": "username",
                "id_field": fields.serializers.CharField(),
            }
        },
    )
    qs = f.filter(note.__class__.objects.all(), f"user:{user.username}")
    assert list(qs) == [note]
