import collections
import logging
import time

import requests
from django.contrib.contenttypes.models import ContentType

from funkwhale_api import musicbrainz
from funkwhale_api.taskapp import celery

from . import models

logger = logging.getLogger(__name__)


def get_tags_from_foreign_key(
    ids, foreign_key_model, foreign_key_attr, tagged_items_attr="tagged_items"
):
    """
    Cf #988, this is useful to tag an artist with #Rock if all its tracks are tagged with
    #Rock, for instance.
    """
    data = {}
    objs = foreign_key_model.objects.filter(
        **{f"{foreign_key_attr}__pk__in": ids}
    ).order_by("-id")
    objs = objs.only("id", f"{foreign_key_attr}_id").prefetch_related(tagged_items_attr)

    for obj in objs.iterator():
        # loop on all objects, store the objs tags + counter on the corresponding foreign key
        row_data = data.setdefault(
            getattr(obj, f"{foreign_key_attr}_id"),
            {"total_objs": 0, "tags": []},
        )
        row_data["total_objs"] += 1
        for ti in getattr(obj, tagged_items_attr).all():
            row_data["tags"].append(ti.tag_id)

    # now, keep only tags that are present on all objects, i.e tags where the count
    # matches total_objs
    final_data = {}
    for key, row_data in data.items():
        counter = collections.Counter(row_data["tags"])
        tags_to_keep = sorted(
            [t for t, c in counter.items() if c >= row_data["total_objs"]]
        )
        if tags_to_keep:
            final_data[key] = tags_to_keep
    return final_data


def add_tags_batch(data, model, tagged_items_attr="tagged_items"):
    model_ct = ContentType.objects.get_for_model(model)
    tagged_items = [
        models.TaggedItem(tag_id=tag_id, content_type=model_ct, object_id=obj_id)
        for obj_id, tag_ids in data.items()
        for tag_id in tag_ids
    ]

    return models.TaggedItem.objects.bulk_create(tagged_items, batch_size=2000)


BASE_URL = "https://musicbrainz.org/ws/2/genre/all"
HEADERS = {"Accept": "application/json"}


def fetch_musicbrainz_genre():
    genres = []
    limit = 100  # Maximum limit per request
    offset = 0

    while True:
        response = requests.get(
            BASE_URL, headers=HEADERS, params={"limit": limit, "offset": offset}
        )

        if "Your requests are exceeding the allowable rate limit" in {
            response._content
        }:
            time.sleep(10)
            response = requests.get(
                BASE_URL, headers=HEADERS, params={"limit": limit, "offset": offset}
            )
            if response.status_code != 200:
                logger.info(f"Failed to fetch mb genre: {response._content}")
                break
        elif response.status_code != 200:
            logger.info(f"Failed to fetch mb genre: {response._content}")
            break

        data = response.json()
        genres.extend(data["genres"])

        # Check if we have fetched all genres
        if offset + limit >= data["genre-count"]:
            break

        offset += limit
        # mb only allow one request per second
        time.sleep(1)

    return genres


@celery.app.task(name="tags.update_musicbrainz_genre")
def update_musicbrainz_genre():
    tags_mbid = models.Tag.objects.all().values_list("mbid", flat=True)
    genres = fetch_musicbrainz_genre()
    for genre in genres:
        if genre["id"] in tags_mbid:
            continue

        create_defaults = {"name": genre["name"], "mbid": genre["id"]}
        models.Tag.objects.update_or_create(
            name=genre["name"],
            defaults=create_defaults,
        )


def sync_fw_item_tag_with_musicbrainz_tags(obj):
    if obj.__class__.__name__ == "Track":
        response = musicbrainz.api.recordings.get(id=obj.mbid, includes=["tags"])
        mb_obj_type = "recording"
    elif obj.__class__.__name__ == "Album":
        response = musicbrainz.api.releases.get(
            id=obj.mbid, includes=["tags", "release-groups"]
        )
        mb_obj_type = "release"
        if mbid := response["release"].get("release-group", {}).get("id", False):
            response["release"]["tag-list"].extend(
                musicbrainz.api.release_groups.get(id=mbid, includes=["tags"])[
                    "release-group"
                ]["tag-list"]
            )

    elif obj.__class__.__name__ == "Artist":
        response = musicbrainz.api.artists.get(id=obj.mbid, includes=["tags"])
        mb_obj_type = "artist"

    tags = [t["name"] for t in response[mb_obj_type]["tag-list"]]

    models.add_tags(obj, *tags)
