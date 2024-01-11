from django.urls import reverse


def test_can_resolve_upload_urls():
    url = reverse("api:v2:upload-groups-list")
    assert url == "/api/v2/upload-groups"
