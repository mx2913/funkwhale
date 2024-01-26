from rest_framework import negotiation, renderers
from defusedxml import ElementTree as etree


# for the django test api client
class PlaylistXspfRenderer(renderers.BaseRenderer):
    media_type = "application/octet-stream"
    format = "xspf"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        root = etree.fromstring(data)
        return etree.tostring(root)
