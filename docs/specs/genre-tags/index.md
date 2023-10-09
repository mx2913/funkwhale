# Genre tags

## The issue

Funkwhale offers users a facility to assign genre tags to items such as tracks, albums, and artists. The `tags_tag` table is populated automatically when new tags are found in uploaded content, and users can also enter custom tags. By default, the table is empty. This means that a user on a new pod won't see any results when attempting to tag items in the frontend.

## The solution

To provide the best experience for new Funkwhale users, we should prepopulate this table with [genre tags from Musicbrainz](https://musicbrainz.org/genres). Doing this enables users to easily search for and select the tags they want to assign to their content without needing to create custom tags or upload tagged content.

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

```url
https://musicbrainz.org/ws/2/genre/all
```

This endpoint accepts the `application/json` header for a JSON response. See the [Musicbrainz API documentation](https://musicbrainz.org/doc/MusicBrainz_API) for more information.

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
