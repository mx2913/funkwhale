import click

from django.db import transaction

from funkwhale_api.users import models
from funkwhale_api.users import serializers

from . import base
from . import utils


class FakeRequest(object):
    def __init__(self, session={}):
        self.session = session


@transaction.atomic
def handler_create_user(
    username, password, email, is_superuser=False, is_staff=False, permissions=[]
):
    serializer = serializers.RS(
        data={
            "username": username,
            "email": email,
            "password1": password,
            "password2": password,
        }
    )
    utils.logger.debug("Validating user data…")
    serializer.is_valid(raise_exception=True)

    # Override email validation, we assume accounts created from CLI have a valid email
    request = FakeRequest(session={"account_verified_email": email})
    utils.logger.debug("Creating user…")
    user = serializer.save(request=request)
    utils.logger.debug("Setting permissions and other attributes…")
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    for permission in permissions:
        if permission in models.PERMISSIONS:
            utils.logger.debug("Setting %s permission to True", permission)
            setattr(user, "permission_{}".format(permission), True)
        else:
            utils.logger.warn("Unknown permission %s", permission)
    utils.logger.debug("Creating actor…")
    user.actor = models.create_actor(user)
    user.save()
    return user


@base.cli.group()
def users():
    """Manage users"""
    pass


@users.command()
@click.argument("username")
@click.option(
    "-p",
    "--password",
    envvar="PASSWORD",
    help="If not provided, a random password will be generated and displayed in console output",
)
@click.option(
    "-e", "--email", help="Email address to associate with the account", required=True,
)
@click.option(
    "--superuser/--no-superuser", default=False,
)
@click.option(
    "--staff/--no-staff", default=False,
)
@click.option(
    "--permission", multiple=True,
)
def create(username, password, email, superuser, staff, permission):
    """Create a new user"""
    generated_password = None
    if not password:
        generated_password = models.User.objects.make_random_password()
    user = handler_create_user(
        username=username,
        password=password or generated_password,
        email=email,
        is_superuser=superuser,
        is_staff=staff,
        permissions=permission,
    )
    click.echo("User {} created!".format(user.username))
    if generated_password:
        click.echo("  Generated password: {}".format(generated_password))
