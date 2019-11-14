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
