import collections

from rest_framework import throttling as rest_throttling

from django.conf import settings


def get_ident(request):
    if hasattr(request, "user") and request.user.is_authenticated:
        return {"type": "authenticated", "id": request.user.pk}
    ident = rest_throttling.BaseThrottle().get_ident(request)

    return {"type": "anonymous", "id": ident}


def get_cache_key(scope, ident):
    parts = ["throttling", scope, ident["type"], str(ident["id"])]
    return ":".join(parts)


def get_scope_for_action_and_ident_type(action, ident_type, view_conf={}):
    config = collections.ChainMap(view_conf, settings.THROTTLING_SCOPES)

    try:
        action_config = config[action]
    except KeyError:
        action_config = config.get("*", {})

    try:
        return action_config[ident_type]
    except KeyError:
        return


class FunkwhaleThrottle(rest_throttling.SimpleRateThrottle):
    def __init__(self):
        pass

    def get_cache_key(self, request, view):
        return get_cache_key(self.scope, self.ident)

    def allow_request(self, request, view):
        self.request = request
        self.ident = get_ident(request)
        action = getattr(view, "action", "*")
        view_scopes = getattr(view, "throttling_scopes", {})
        if view_scopes is None:
            return True
        self.scope = get_scope_for_action_and_ident_type(
            action=action, ident_type=self.ident["type"], view_conf=view_scopes
        )
        if not self.scope or self.scope not in settings.THROTTLING_RATES:
            return True
        self.rate = settings.THROTTLING_RATES[self.scope]
        self.num_requests, self.duration = self.parse_rate(self.rate)
        self.request = request

        return super().allow_request(request, view)

    def attach_info(self):
        info = {
            "num_requests": self.num_requests,
            "duration": self.duration,
            "scope": self.scope,
            "history": self.history or [],
            "wait": self.wait(),
        }
        setattr(self.request, "_throttle_status", info)

    def throttle_success(self):
        self.attach_info()
        return super().throttle_success()

    def throttle_failure(self):
        self.attach_info()
        return super().throttle_failure()
