import operator

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.permissions import BasePermission

from funkwhale_api.common import preferences


class ConditionalAuthentication(BasePermission):
    def has_permission(self, request, view):
        if preferences.get("common__api_authentication_required"):
            return (request.user and request.user.is_authenticated) or (
                hasattr(request, "actor") and request.actor
            )
        return True


class OwnerPermission(BasePermission):
    """
    Ensure the request user is the owner of the object.

    Usage:

    class MyView(APIView):
        model = MyModel
        permission_classes = [OwnerPermission]
        owner_field = 'owner'
        owner_checks = ['read', 'write']
    """

    perms_map = {
        "GET": "read",
        "OPTIONS": "read",
        "HEAD": "read",
        "POST": "write",
        "PUT": "write",
        "PATCH": "write",
        "DELETE": "write",
    }

    def has_object_permission(self, request, view, obj):
        method_check = self.perms_map[request.method]
        owner_checks = getattr(view, "owner_checks", ["read", "write"])
        if method_check not in owner_checks:
            # check not enabled
            return True

        owner_field = getattr(view, "owner_field", "user")
        owner_exception = getattr(view, "owner_exception", Http404)
        try:
            owner = operator.attrgetter(owner_field)(obj)
        except ObjectDoesNotExist:
            raise owner_exception

        if not owner or not request.user.is_authenticated or owner != request.user:
            raise owner_exception
        return True


class PrivacyLevelPermission(BasePermission):
    """
    Ensure the request user have acces to the object considering the privacylevel configuration
    of the user. Could be expanded to other objects type.
    """

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "user"):
            # to do : it's a remote actor. We could trigger an update of the remote actor data
            # to avoid leaking data
            return True
        if obj.user.privacy_level == "everyone":
            return True
        # user is anonymous
        elif not hasattr(request.user, "actor"):
            return False
        elif obj.user.privacy_level == "instance":
            # user is local
            if hasattr(request.user, "actor"):
                return True
            elif request.actor.is_local():
                return True
            else:
                return False

        elif obj.user.privacy_level == "me" and obj.user.actor == request.user.actor:
            return True

        elif (
            obj.user.privacy_level == "followers"
            and request.user.actor in obj.user.actor.get_followers()
        ):
            return True
        else:
            return False
