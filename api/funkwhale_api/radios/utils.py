import json
import logging

import requests

logger = logging.getLogger(__name__)

VALID_METRICS = [
    "mfccs",
    "mfccsw",
    "gfccs",
    "gfccsw",
    "key",
    "bpm",
    "onsetrate",
    "moods",
    "instruments",
    "dortmund",
    "rosamerica",
    "tzanetakis"
]


class EndpointError(Exception):
    pass


def get_similar_tracks_mbids_from_mbid(mbid, annoy_similarity):

    if annoy_similarity not in VALID_METRICS:
        raise AttributeError(
            "Metric %s is not valid. Must be one of : " + print(VALID_METRICS)
        )

    headers = {"Content-Type': 'application/json"}
    endpoint = "acousticbrainz.org/api/v1/similarity"
    similar_tracks_mbids = []
    similar_tracks = requests.get(
        "https://{endpoint}/{annoy_similarity}/?recording_ids={mbid}&remove_dups&n_neighbours=1000"
        .format(
            endpoint=endpoint, annoy_similarity=annoy_similarity, mbid=mbid
        ),
        headers=headers
    )
    if similar_tracks.status_code != 200:
        logger.warning("Error while querying {endpoint!r} : {similar_tracks.content!r}")
        raise EndpointError

    j = json.loads(similar_tracks.content)
    for tracks in j["{mbid}".format(mbid=mbid)]["0"]:
        similar_tracks_mbids.append(tracks["recording_mbid"])
    return similar_tracks_mbids
