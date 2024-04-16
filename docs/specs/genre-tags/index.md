# Genre tags

## The issue

Funkwhale offers users a facility to assign genre tags to items such as tracks, albums, and artists. The `tags_tag` table is populated automatically when new tags are found in uploaded content, and users can also enter custom tags. By default, the table is empty. This means that a user on a new pod won't see any results when attempting to tag items in the frontend.

## The solution

To provide the best experience for new Funkwhale users, we should pre-populate this table with [genre tags from Musicbrainz](https://musicbrainz.org/genres). Doing this enables users to easily search for and select the tags they want to assign to their content without needing to create custom tags or upload tagged content.

Having these tags easily available also facilitates better tagging within Funkwhale in future, reducing the reliance on external tools such as Picard.

## Feature behavior

### Backend behavior

The `tags_tag` table contains the following fields:

| Field            | Data type                | Description                                                                                                             | Relations                            | Constraints    |
| ---------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | -------------- |
| `id`             | Integer                  | The randomly generated table ID                                                                                         | `tags_taggeditem.tag_id` foreign key | None           |
| `musicbrainz_id` | UUID                     | The Musicbrainz genre tag `id`. Used to identify the tag in Musicbrainz fetches                                         | None                                 | None           |
| `name`           | String                   | The name of the tag. Assigned by Funkwhale during creation for use in URLs. Uses Pascal casing for consistency          | None                                 | Must be unique |
| `display_name`   | String                   | The name of the tag as the user entered it or as it was originally written by Musicbrainz. Lowercase, normalizes spaces | None                                 | None           |
| `creation_date`  | Timestamp with time zone | The date on which the tag was created                                                                                   | None                                 | None           |

#### Musicbrainz fetch task

To keep Funkwhale's database up-to-date with Musicbrainz's genre tags, we must fetch information from Musicbrainz periodically. We can use the following endpoint to fetch the information:

```text
https://musicbrainz.org/ws/2/genre/all
```

This endpoint accepts the `application/json` header for a JSON response. See the [Musicbrainz API documentation](https://musicbrainz.org/doc/MusicBrainz_API) for more information. The pagination can be controlled by passing the following options:

- `limit`: the number of results to return
- `offset`: the starting point of the page

The fetch task should fetch **all** pages, using the response `genre-count` to determine how many offset positions to pass.

```json
{
  "genre-count": 1913,
  "genre-offset": 24,
  "genres": [
    {
      "disambiguation": "",
      "id": "243975aa-1250-4429-8bd3-97080af44cf7",
      "name": "afro trap"
    },
    {
      "name": "afro-cuban jazz",
      "id": "cdb11433-1ff1-4c88-be16-717567e1342f",
      "disambiguation": ""
    },
    {
      "name": "afro-funk",
      "disambiguation": "",
      "id": "fc00175b-2be9-4d73-ba91-27b3ca827223"
    },
    {
      "name": "afro-jazz",
      "disambiguation": "",
      "id": "6f33d775-b4e2-473c-a7db-e34c525cc52d"
    },
    {
      "disambiguation": "",
      "id": "a7e0229c-6e53-45f1-a6f2-a791e78b159e",
      "name": "afro-zouk"
    },
    {
      "disambiguation": "funk/soul + West African sounds",
      "id": "fcc58a18-9326-4c92-8b29-c294d44379c3",
      "name": "afrobeat"
    },
    {
      "id": "b8793fdb-bbc8-4418-a6f8-05eafbbe07ef",
      "disambiguation": "West African urban/pop music",
      "name": "afrobeats"
    },
    {
      "name": "afropiano",
      "id": "d42b567f-0952-424b-959d-bee6e5961cc0",
      "disambiguation": ""
    },
    {
      "disambiguation": "",
      "id": "52349b68-9cad-496e-8785-00d53f410246",
      "name": "afroswing"
    },
    {
      "name": "agbadza",
      "disambiguation": "",
      "id": "c6d1e78b-ac82-4bb8-89d5-21e3226dc906"
    },
    {
      "disambiguation": "",
      "id": "b8ae0a3c-5826-4104-9663-fe8f828effa9",
      "name": "agbekor"
    },
    {
      "name": "aggrotech",
      "disambiguation": "",
      "id": "c844c144-90a8-4288-981e-e38275592688"
    },
    {
      "name": "ahwash",
      "id": "4802e6e4-f403-41d1-8e58-76e5cf4df81d",
      "disambiguation": ""
    },
    {
      "id": "50cc5641-b4f9-40b7-bf7a-6d903ac6c1c5",
      "disambiguation": "",
      "name": "aita"
    },
    {
      "id": "aebbce35-0e8b-40e9-b04c-bebbbda124d0",
      "disambiguation": "",
      "name": "akishibu-kei"
    },
    {
      "name": "al jeel",
      "disambiguation": "",
      "id": "0f8d3ff4-8cda-42c4-b462-10352cd01606"
    },
    {
      "name": "algerian chaabi",
      "id": "998efb76-2f98-41c8-8c5f-74c32e405e9f",
      "disambiguation": ""
    },
    {
      "name": "algorave",
      "id": "e0a9d0d1-b86f-4344-82a9-022a84627087",
      "disambiguation": ""
    },
    {
      "name": "alloukou",
      "disambiguation": "",
      "id": "e367c884-d94d-4fba-abc4-8ac51d167ccf"
    },
    {
      "disambiguation": "",
      "id": "ef1d11cc-e70f-4885-ad6c-103f060d33b2",
      "name": "alpenrock"
    },
    {
      "disambiguation": "",
      "id": "5f9cba3d-1a9f-46cd-8c49-7ed78d1f3354",
      "name": "alternative country"
    },
    {
      "name": "alternative dance",
      "id": "8301f73c-9166-4108-bfeb-4fd22dc19083",
      "disambiguation": ""
    },
    {
      "name": "alternative folk",
      "id": "0b48a36c-630f-4ee7-8cf3-480e3dd8be65",
      "disambiguation": ""
    },
    {
      "name": "alternative hip hop",
      "disambiguation": "",
      "id": "924943cd-73c8-45c0-96eb-74f2a15e5d6e"
    },
    {
      "disambiguation": "",
      "id": "7c4d0994-4c49-4c74-8763-df27fc0084cc",
      "name": "alté"
    }
  ]
}
```

The fetch task should run _initially upon first startup_ and then _monthly_ thereafter. The pod admin must be able to disable this job or run it manually at their discretion.

The task should use the following logic:

1. Call the Musicbrainz API to fetch new data
2. Verify the listed entries against the Funkwhale tag table. The `id` field in the response should be checked against the `musicbrainz_id` field
3. Any entries that do not currently exist in Funkwhale should be added with the following mapping:

| Musicbrainz response field | Tags table column | Notes                                                                             |
| -------------------------- | ----------------- | --------------------------------------------------------------------------------- |
| `id`                       | `musicbrainz_id`  |                                                                                   |
| `name`                     | `display_name`    | Funkwhale should automatically generate a Pascal cased `name` based on this entry |

4. If the `display_name` of a tag **exactly matches** a `name` in the Musicbrainz response but the tag has no `musicbrainz_id`, the `musicbrainz_id` should be populated

### Frontend behavior

#### Tagged uploads

When a user uploads new content with genre tags, the tagged item should be linked to any existing tags and new ones should be created if they're not found.

#### In-app tagging

When a user uploads new content with _no_ genre tags, they should be able to select tags from a dropdown menu. This menu is populated with the tags from the database with the `display_name` shown in the list. When a tag is selected, the item is linked to the associated tag.

If a user inserts a new tag, Funkwhale should:

1. Store the entered string as the tag's `display_name`
2. Generate a Pascal cased `name` for the tag
3. Associate the targeted object with the new tag

#### Search results

Users should be able to search for tags using Funkwhale's in-app search. In search autocomplete and search results page, the `display_name` should be used. The `name` of the tag should be used to populate the search URL.

#### Cards

The `display_name` of the tag should be shown in pills against cards.

### Admin options

If the admin of a server wants to **disable** MusicBrainz tagging, they should be able to toggle this in their instance settings. If the setting is **disabled**:

- The sync task should stop running
- Any tags with an `musicbrainz_id` should be excluded from API queries.

## Availability

- [x] Admin panel
- [x] App frontend
- [x] CLI

## Responsible parties

- Backend group:
  - Update the tracks table to support the new information
  - Update the API to support the new information, or create a new v2 endpoint
  - Create the new fetch task
  - Add admin controls for the new task
- Frontend group:
  - Update views to use `display_name` instead of `name` for tag results
  - Update API calls to use the new API structure created by the backend group
- Documentation group:
  - Document the new task and settings for admins
