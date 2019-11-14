import pytest

from funkwhale_api.cli import users


def test_user_create_handler(factories, mocker, now):
    kwargs = {
        "username": "helloworld",
        "password": "securepassword",
        "is_superuser": False,
        "is_staff": True,
        "email": "hello@world.email",
        "permissions": ["moderation"],
    }
    set_password = mocker.spy(users.models.User, "set_password")
    create_actor = mocker.spy(users.models, "create_actor")
    user = users.handler_create_user(**kwargs)

    assert user.username == kwargs["username"]
    assert user.is_superuser == kwargs["is_superuser"]
    assert user.is_staff == kwargs["is_staff"]
    assert user.date_joined >= now
    set_password.assert_called_once_with(user, kwargs["password"])
    create_actor.assert_called_once_with(user)

    expected_permissions = {
        p: p in kwargs["permissions"] for p in users.models.PERMISSIONS
    }

    assert user.all_permissions == expected_permissions


def test_user_delete_handler_soft(factories, mocker, now):
    user1 = factories["federation.Actor"](local=True).user
    actor1 = user1.actor
    user2 = factories["federation.Actor"](local=True).user
    actor2 = user2.actor
    user3 = factories["federation.Actor"](local=True).user
    delete_account = mocker.spy(users.tasks, "delete_account")
    users.handler_delete_user([user1.username, user2.username, "unknown"])

    assert delete_account.call_count == 2
    delete_account.assert_any_call(user_id=user1.pk)
    with pytest.raises(user1.DoesNotExist):
        user1.refresh_from_db()

    delete_account.assert_any_call(user_id=user2.pk)
    with pytest.raises(user2.DoesNotExist):
        user2.refresh_from_db()

    # soft delete, actor shouldn't be deleted
    actor1.refresh_from_db()
    actor2.refresh_from_db()

    # not deleted
    user3.refresh_from_db()


def test_user_delete_handler_hard(factories, mocker, now):
    user1 = factories["federation.Actor"](local=True).user
    actor1 = user1.actor
    user2 = factories["federation.Actor"](local=True).user
    actor2 = user2.actor
    user3 = factories["federation.Actor"](local=True).user
    delete_account = mocker.spy(users.tasks, "delete_account")
    users.handler_delete_user([user1.username, user2.username, "unknown"], soft=False)

    assert delete_account.call_count == 2
    delete_account.assert_any_call(user_id=user1.pk)
    with pytest.raises(user1.DoesNotExist):
        user1.refresh_from_db()

    delete_account.assert_any_call(user_id=user2.pk)
    with pytest.raises(user2.DoesNotExist):
        user2.refresh_from_db()

    # hard delete, actors are deleted as well
    with pytest.raises(actor1.DoesNotExist):
        actor1.refresh_from_db()

    with pytest.raises(actor2.DoesNotExist):
        actor2.refresh_from_db()

    # not deleted
    user3.refresh_from_db()
