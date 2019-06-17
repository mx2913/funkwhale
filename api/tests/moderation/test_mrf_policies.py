import pytest

from funkwhale_api.moderation import mrf
from funkwhale_api.moderation import mrf_policies


@pytest.mark.parametrize(
    "enabled, payload, kwargs, allowed_domains, expected",
    [
        # allow listing enabled, domain on allowed list
        (
            True,
            {"id": "http://allowed.domain"},
            {"sender_id": "http://allowed.domain/actor"},
            ["allowed.domain"],
            None,
        ),
        # allow listing enabled, domain NOT on allowed list
        (
            True,
            {"id": "http://allowed.domain"},
            {"sender_id": "http://allowed.domain/actor"},
            [],
            mrf.Discard,
        ),
        # allow listing disabled
        (
            False,
            {"id": "http://allowed.domain"},
            {"sender_id": "http://allowed.domain/actor"},
            [],
            mrf.Skip,
        ),
        # multiple domains to check, failure
        (
            True,
            {"id": "http://allowed.domain"},
            {"sender_id": "http://notallowed.domain/actor"},
            ["allowed.domain"],
            mrf.Discard,
        ),
        # multiple domains to check, success
        (
            True,
            {"id": "http://allowed.domain"},
            {"sender_id": "http://anotherallowed.domain/actor"},
            ["allowed.domain", "anotherallowed.domain"],
            None,
        ),
    ],
)
def test_allow_list_policy(
    enabled, payload, kwargs, expected, allowed_domains, preferences, factories
):
    preferences["moderation__allow_list_enabled"] = enabled
    for d in allowed_domains:
        factories["federation.Domain"](name=d, allowed=True)

    if expected:
        with pytest.raises(expected):
            mrf_policies.check_allow_list(payload, **kwargs)
    else:
        assert mrf_policies.check_allow_list(payload, **kwargs) == expected
