# to do : to delete
# import pytest
# from django.test import Client
# from django.urls import reverse

# from funkwhale_api.common import serializers as common_serializers
# from funkwhale_api.common import utils as common_utils
# from funkwhale_api.moderation import tasks as moderation_tasks
# from funkwhale_api.users.models import User


# def test_can_follow_user(factories, logged_in_api_client, mocker):
#     followed_user = factories["users.User"]()
#     actor = factories["federation.Actor"]()
#     logged_in_api_client.user.actor = actor
#     url = reverse("api:v2:users:users-follow-requests", kwargs={"pk": followed_user.pk})
#     routes = mocker.patch("funkwhale_api.federation.api_views.routes.outbox.dispatch")
#     response = logged_in_api_client.post(url)
#     assert response.status_code == 204
#     assert routes.call_count == 1


# def test_can_unfollow(factories, logged_in_api_client, mocker):
#     logged_in_api_client.user.create_actor()
#     followed_user = factories["users.User"](with_actor=True)
#     user_follow = factories["federation.UserFollow"](
#         target=followed_user, actor=logged_in_api_client.user.actor
#     )
#     url = reverse("api:v2:users:users-unfollow", kwargs={"pk": followed_user.pk})
#     routes = mocker.patch("funkwhale_api.federation.api_views.routes.outbox.dispatch")
#     response = logged_in_api_client.post(url)
#     assert response.status_code == 200


# #  /users/id/follow_requests/
# # def test_can_patch_follow_user(factories, logged_in_api_client, mocker):
# #     logged_in_api_client.user.create_actor()
# #     following_user = factories["users.User"](with_actor=True)
# #     url = reverse(
# #         "api:v2:users:users-follow-requests",
# #         kwargs={"pk": logged_in_api_client.user.pk},
# #     )
# #     routes = mocker.patch("funkwhale_api.federation.api_views.routes.outbox.dispatch")
# #     data = {
# #         "approved": True,
# #         "actor": following_user.actor,
# #         "target": logged_in_api_client.user.pk,
# #     }
# #     response = logged_in_api_client.patch(url, data=data)
# #     assert response.status_code == 204
# #     assert routes.call_count == 1


# def test_can_patch_follow_user_v2(factories, logged_in_api_client, mocker):
#     logged_in_api_client.user.create_actor()
#     following_user = factories["users.User"](with_actor=True)
#     user_follow = factories["federation.UserFollow"](
#         target=following_user, actor=following_user.actor
#     )
#     url = reverse(
#         "api:v2:users:follow_request_patch",
#         kwargs={
#             "user_pk": logged_in_api_client.user.pk,
#             "follow_pk": user_follow.pk,
#         },
#     )
#     routes = mocker.patch("funkwhale_api.federation.api_views.routes.outbox.dispatch")
#     data = {
#         "approved": True,
#     }
#     response = logged_in_api_client.patch(url, data=data, format="json")
#     assert response.status_code == 204
#     assert routes.call_count == 1


# # def test_only_target_user_can_patch_follow_user(factories, logged_in_api_client):
# #     logged_in_api_client.user.create_actor()
# #     followed_user = factories["users.User"]()
# #     url = reverse("api:v2:users:users-follow-requests", kwargs={"pk": followed_user.pk})
# #     data = {
# #         "approved": True,
# #         "actor": logged_in_api_client.user.actor,
# #         "target": followed_user.pk,
# #     }
# #     response = logged_in_api_client.patch(url, data=data)
# #     assert response.status_code == 403


# def test_can_get_my_userfollowings(factories, logged_in_api_client, mocker):
#     logged_in_api_client.user.create_actor()
#     followed_user = factories["users.User"](with_actor=True)
#     user_follow = factories["federation.UserFollow"](
#         actor=logged_in_api_client.user.actor, target=followed_user
#     )
#     url = reverse(
#         "api:v2:users:users-followings", kwargs={"pk": logged_in_api_client.user.pk}
#     )
#     response = logged_in_api_client.get(url)
#     assert response.status_code == 200
#     assert str(user_follow.uuid) == response.data["results"][0]["uuid"]


# def test_can_get_user_public_profile_userfollowings(
#     factories, logged_in_api_client, mocker
# ):
#     logged_in_api_client.user.create_actor()
#     following_user = factories["users.User"](with_actor=True, privacy_level="public")
#     user_follow = factories["federation.UserFollow"](actor=following_user.actor)
#     url = reverse("api:v2:users:users-followings", kwargs={"pk": following_user.pk})
#     response = logged_in_api_client.get(url)
#     assert response.status_code == 200
#     assert str(user_follow.uuid) == response.data["results"][0]["uuid"]


# def test_cannot_get_user_private_profile_userfollowings(
#     factories, logged_in_api_client, mocker
# ):
#     logged_in_api_client.user.create_actor()
#     following_user = factories["users.User"](with_actor=True, privacy_level="private")
#     user_follow = factories["federation.UserFollow"](actor=following_user.actor)
#     url = reverse("api:v2:users:users-followings", kwargs={"pk": following_user.pk})
#     response = logged_in_api_client.get(url)
#     assert response.status_code == 403


# def test_can_get_user_pod_profile_userfollowings(
#     factories, logged_in_api_client, mocker
# ):
#     logged_in_api_client.user.create_actor()
#     following_user = factories["users.User"](with_actor=True, privacy_level="pod")
#     user_follow = factories["federation.UserFollow"](actor=following_user.actor)
#     url = reverse("api:v2:users:users-followings", kwargs={"pk": following_user.pk})
#     response = logged_in_api_client.get(url)
#     assert response.status_code == 200


# def test_cannot_get_user_pod_profile_userfollowings(
#     factories, logged_in_api_client, mocker
# ):
#     factories["federation.Domain"](name="notatalllocal")
#     logged_in_api_client.user.create_actor(domain_id="notatalllocal")
#     following_user = factories["users.User"](with_actor=True, privacy_level="pod")
#     user_follow = factories["federation.UserFollow"](actor=following_user.actor)
#     url = reverse("api:v2:users:users-followings", kwargs={"pk": following_user.pk})
#     response = logged_in_api_client.get(url)
#     assert response.status_code == 403


# def test_can_get_my_followers(factories, logged_in_api_client, mocker):
#     following_user = factories["users.User"](with_actor=True)
#     user_follow = factories["federation.UserFollow"](
#         target=logged_in_api_client.user, actor=following_user.actor
#     )
#     url = reverse(
#         "api:v2:users:users-followers", kwargs={"pk": logged_in_api_client.user.pk}
#     )
#     response = logged_in_api_client.get(url)
#     assert response.status_code == 200
#     assert str(user_follow.uuid) == response.data["results"][0]["uuid"]


# # to do : do this through should_autoapprove_follow     autoapprove = serializer.validated_data["object"].should_autoapprove_follow(
# def test_follow_public_user_autoapprove(factories, logged_in_api_client, mocker):
#     logged_in_api_client.user.create_actor()
#     followed_user = factories["users.User"](with_actor=True, privacy_level="public")
#     url = reverse("api:v2:users:users-follow-requests", kwargs={"pk": followed_user.pk})
#     routes = mocker.patch("funkwhale_api.federation.api_views.routes.outbox.dispatch")
#     response = logged_in_api_client.post(url)
#     assert response.status_code == 204
#     assert routes.call_count == 1
