import os

os.environ.setdefault("FUNKWHALE_URL", "http://funkwhale.dev")

from .common import *  # noqa

DEBUG = True
SECRET_KEY = "a_super_secret_key!"
TYPESENSE_API_KEY = "apikey"
REST_FRAMEWORK = {
    "TEST_REQUEST_RENDERER_CLASSES": [
        "rest_framework.renderers.MultiPartRenderer",
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.TemplateHTMLRenderer",
        "funkwhale_api.playlists.renderers.PlaylistXspfRenderer",
    ],
}
