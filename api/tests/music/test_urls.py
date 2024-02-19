import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    "input,args,expected_url",
    [
        ("api:v2:upload-groups-list", None, "/api/v2/upload-groups"),
        (
            "api:v2:upload-groups-uploads",
            ["1234-1234-1234"],
            "/api/v2/upload-groups/1234-1234-1234/uploads",
        ),
    ],
)
def test_can_resolve_upload_urls(input, args, expected_url):
    url = reverse(input, args=args)
    assert url == expected_url
