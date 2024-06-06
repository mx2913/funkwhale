import django_filters

from funkwhale_api.common import filters as common_filters
from funkwhale_api.moderation import filters as moderation_filters

from . import models


class ListeningFilter(moderation_filters.HiddenContentFilterSet):
    username = django_filters.CharFilter("actor__user__username")
    domain = django_filters.CharFilter("actor__domain_id")
    scope = common_filters.ActorScopeFilter(actor_field="actor", distinct=True)

    class Meta:
        model = models.Listening
        hidden_content_fields_mapping = moderation_filters.USER_FILTER_CONFIG[
            "LISTENING"
        ]
        fields = []
