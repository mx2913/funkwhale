import datetime
import logging

import pylistenbrainz
import pytest

from django.utils import timezone

from funkwhale_api.contrib.listenbrainz import tasks
from funkwhale_api.history import models as history_models


def test_trigger_listening_sync_with_listenbrainz():
    # to do
    pass
