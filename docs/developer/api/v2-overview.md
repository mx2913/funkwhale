# API v2 overview

To ensure that Funkwhale's v2 REST API is consistent and scalable, we need to ensure that certain rules are followed when implementing endpoints. The basic rules are covered in this document.

## Appropriate naming conventions

In keeping with best practice, Funkwhale's API follows these naming conventions:

1. All endpoints should start with the **collection** that the endpoint represents. For example: `artist`, `release`, `recording`.
2. The specificity of an endpoint's target should be set by the path. For example: `artist/{guid}`.
3. Any endpoints that represent multi-word entities should be rendered in kebab case (`kebab-case`). For example: `/api/v2/release-group`
4. Endpoint names should only ever be _nouns_. Any verb representing the action should be described by the HTTP action. For example: `GET`, `POST`, `PATCH`, `DELETE`
5. Multi-word properties in entity representations should be rendered in camel case (`camelCase`) to maintain consistency with other endpoints such as nodeinfo
6. Multi-word parameters in API queries should be rendered in in snake case (`snake_case`) to avoid issues with URL formatting

## Generic entity naming conventions

To make Funkwhale more scalable, entities should be given more generic names. For example: instead of using music-specific naming conventions such as `Album`, a generic term like `Release` should be substituted. Since many audio properties can be referred to as a `Release` (such as albums, audiobooks, DJ sets, podcast series), this naming convention can scale where the old one could not.

Where appropriate, Funkwhale should follow the same conventions [put forward by MusicBrainz](https://musicbrainz.org/doc/MusicBrainz_Entity). These entities are well-defined generic concepts with room for extension, and following them makes Funkwhale's interactions with MusicBrainz much simpler.

## Deprecation of database IDs

Several endpoints in API v1 use database IDs (integers) to refer to items such as artists and tracks. However, it's best practice to use GUIDs wherever a unique identifier is needed. API v2 should always use GUIDs to refer to items rather than relying on the database IDs.

## Atomic transactions

Per REST conventions, all requests must either **succeed** or **fail** as a whole. This means that if a `POST` request is made and any part of the process fails, the entire transaction must roll back and no changes can be committed. The requester must be informed of the issue with a meaningful error message.

To facilitate this, `POST` and `PATCH` actions must target **one item at a time**. Instead of allowing users to create multiple items in a single `POST` request represented by an array, the Funkwhale API should instead accept only one object in any request. While this increases the number of calls that must be sent to the API, it also increases Funkwhale's ability to communicate any issues with the requester in a timely manner.

## Serializer inheritance

Serializers representing Funkwhale entities should always inherit from a _minimal_ (`Base`) serializer. This ensures that when new critical information is added to a serializer it is inherited.

For example: a `BaseRelease` serializes only the most essential information about a release for displaying information about it.

```json
{
  "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "fid": "string",
  "mbid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "string",
  "artistCredit": [
    {
      "name": "string",
      "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "joinPhrase": "string"
    }
  ],
  "playable": true,
  "cover": {
    "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "mimetype": "string",
    "size": 0,
    "creationDate": "2023-11-19T01:44:10.981Z",
    "urls": {
      "source": "string",
      "original": "string"
    }
  }
}
```

The `Release` serializer inherits all information from the `BaseRelease` serializer and appends additional information pertaining to the release, including the creation date, release date, and associated release group.

```json
{
  "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "fid": "string",
  "mbid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "string",
  "artistCredit": [
    {
      "name": "string",
      "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "joinPhrase": "string"
    }
  ],
  "playable": true,
  "cover": {
    "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "mimetype": "string",
    "size": 0,
    "creationDate": "2023-11-19T01:43:07.746Z",
    "urls": {
      "source": "string",
      "original": "string"
    }
  },
  "creationDate": "2023-11-19T01:43:07.746Z",
  "releaseDate": "2023-11-19",
  "trackCount": 0,
  "duration": 0,
  "attributedTo": {
    "fid": "string",
    "fullUsername": "string",
    "preferredUsername": "string",
    "name": "string",
    "domain": "string",
    "local": true
  },
  "local": true,
  "releaseGroup": {
    "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "string",
    "primaryType": "album",
    "releaseVersions": 0
  },
  "tracks": [
    {
      "recording": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "entryNumber": 0,
      "position": 0
    }
  ]
}
```

By maintaining this `Base` serializer, we can ensure any essential information is contained in both the `Base` representation and the full complex representation shown on dedicated endpoints.

When displaying interface elements such as cards or search results, the `Base` version of the serializer should be used. For example:

- When calling for a list of `Release` objects to render cards, the `BaseRelease` serializer is used (`/api/v2/releases`)
- When navigating to the overview page for a release, the full `Release` serializer is used (`/api/v2/releases/{guid}`)

## Reduced duplication in serializers

Funkwhale API v1 has a lot of duplicated data in certain responses due to how the serializers are configured. For example:

- A `Listening` object contains the following information:
  - The `User` who recorded the `Listening`
  - The `Actor` of the `User`
  - The `Track`. This contains:
    - The `Artist` attributed to the `Track`
    - The `Album` that contains the `Track`. This contains:
      - The `Artist` attributed to the `Album`

Since the `Listening` serializer inherits the full serializer for each of these entities, the resulting response is large and contains a lot of duplicated information.

```json
{
  "id": 52808,
  "user": {
    "id": 1,
    "username": "doctorworm",
    "name": "",
    "date_joined": "2018-12-12T21:03:28Z",
    "avatar": {
      "uuid": "d0af4fe3-d420-4e98-87d3-2d1cc3f7cdc5",
      "size": 3834756,
      "mimetype": "image/jpeg",
      "creation_date": "2022-12-28T09:43:20.460502Z",
      "urls": {
        "source": null,
        "original": "https://fra1.digitaloceanspaces.com/tanukitunes/attachments/87/b0/1d/adjust_portrait_0000_img00465_ciaran_a.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=8167aae2f71896192ec718ff7849e2828b3d1a04c75a7a1b02e8e5a36d08e582",
        "medium_square_crop": "https://fra1.digitaloceanspaces.com/tanukitunes/__sized__/attachments/87/b0/1d/adjust_portrait_0000_img00465_ciaran_a-crop-c0-5__0-5-200x200-95.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=a035aead373e5537aa94af8fe29b7fc9ab5c0edcd4d5d1c15a15ced420ddfbae",
        "large_square_crop": "https://fra1.digitaloceanspaces.com/tanukitunes/__sized__/attachments/87/b0/1d/adjust_portrait_0000_img00465_ciaran_a-crop-c0-5__0-5-600x600-95.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=49f25fb7cccd0a617579b74f59ab929dbac76838c3c57310d9058b205c5bd7ed"
      }
    }
  },
  "track": {
    "artist": {
      "id": 14,
      "fid": "https://tanukitunes.com/federation/music/artists/728f9e77-a553-41d6-9d83-e5d78fcd2563",
      "mbid": "183d6ef6-e161-47ff-9085-063c8b897e97",
      "name": "They Might Be Giants",
      "creation_date": "2018-12-13T00:08:02.252126Z",
      "modification_date": "2020-03-19T15:05:32.179932Z",
      "is_local": true,
      "content_category": "music",
      "description": {
        "text": "They Might Be Giants (often abbreviated as TMBG) is an American alternative rock band formed in 1982 by John Flansburgh and John Linnell. During TMBG's early years, Flansburgh and Linnell frequently performed as a duo, often accompanied by a drum machine. In the early 1990s, TMBG expanded to include a backing band. The duo's current backing band consists of Marty Beller, Dan Miller, and Danny Weinkauf. The group is known for their uniquely experimental and absurdist style of alternative music, typically utilising surreal, humorous lyrics and unconventional instruments in their songs. Over their career, they have found success on the modern rock and college radio charts. They have also found success in children's music, and in theme music for several television programs and films.",
        "content_type": "text/markdown",
        "html": "<p>They Might Be Giants (often abbreviated as TMBG) is an American alternative rock band formed in 1982 by John Flansburgh and John Linnell. During TMBG's early years, Flansburgh and Linnell frequently performed as a duo, often accompanied by a drum machine. In the early 1990s, TMBG expanded to include a backing band. The duo's current backing band consists of Marty Beller, Dan Miller, and Danny Weinkauf. The group is known for their uniquely experimental and absurdist style of alternative music, typically utilising surreal, humorous lyrics and unconventional instruments in their songs. Over their career, they have found success on the modern rock and college radio charts. They have also found success in children's music, and in theme music for several television programs and films.</p>"
      },
      "attachment_cover": {
        "uuid": "5e918c69-9a28-4dda-b2ba-bec9ed7ade97",
        "size": 450338,
        "mimetype": "image/jpeg",
        "creation_date": "2020-01-17T17:13:28.131126Z",
        "urls": {
          "source": null,
          "original": "https://fra1.digitaloceanspaces.com/tanukitunes/attachments/9f/47/fb/tmbg.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=d80640f390c9984a942a951c06a28456efafe6136d2dee53b001e551b8836ec4",
          "medium_square_crop": "https://fra1.digitaloceanspaces.com/tanukitunes/__sized__/attachments/9f/47/fb/tmbg-crop-c0-5__0-5-200x200-95.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=a0770c764e2242ee203a71f77be6a3de782050bf46b03683dc883be27c679e65",
          "large_square_crop": "https://fra1.digitaloceanspaces.com/tanukitunes/__sized__/attachments/9f/47/fb/tmbg-crop-c0-5__0-5-600x600-95.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=14d604c022fc2b923e8c124c988a5b855e99f35f8a0bf598e9fe7677096fe990"
        }
      },
      "channel": null
    },
    "album": {
      "id": 51,
      "fid": "https://tanukitunes.com/federation/music/albums/d630422f-ce40-4f24-98d1-33dda13248dd",
      "mbid": "459dd621-8f47-4af6-97f7-2f925e685853",
      "title": "The Else",
      "artist": {
        "id": 14,
        "fid": "https://tanukitunes.com/federation/music/artists/728f9e77-a553-41d6-9d83-e5d78fcd2563",
        "mbid": "183d6ef6-e161-47ff-9085-063c8b897e97",
        "name": "They Might Be Giants",
        "creation_date": "2018-12-13T00:08:02.252126Z",
        "modification_date": "2020-03-19T15:05:32.179932Z",
        "is_local": true,
        "content_category": "music",
        "description": {
          "text": "They Might Be Giants (often abbreviated as TMBG) is an American alternative rock band formed in 1982 by John Flansburgh and John Linnell. During TMBG's early years, Flansburgh and Linnell frequently performed as a duo, often accompanied by a drum machine. In the early 1990s, TMBG expanded to include a backing band. The duo's current backing band consists of Marty Beller, Dan Miller, and Danny Weinkauf. The group is known for their uniquely experimental and absurdist style of alternative music, typically utilising surreal, humorous lyrics and unconventional instruments in their songs. Over their career, they have found success on the modern rock and college radio charts. They have also found success in children's music, and in theme music for several television programs and films.",
          "content_type": "text/markdown",
          "html": "<p>They Might Be Giants (often abbreviated as TMBG) is an American alternative rock band formed in 1982 by John Flansburgh and John Linnell. During TMBG's early years, Flansburgh and Linnell frequently performed as a duo, often accompanied by a drum machine. In the early 1990s, TMBG expanded to include a backing band. The duo's current backing band consists of Marty Beller, Dan Miller, and Danny Weinkauf. The group is known for their uniquely experimental and absurdist style of alternative music, typically utilising surreal, humorous lyrics and unconventional instruments in their songs. Over their career, they have found success on the modern rock and college radio charts. They have also found success in children's music, and in theme music for several television programs and films.</p>"
        },
        "attachment_cover": {
          "uuid": "5e918c69-9a28-4dda-b2ba-bec9ed7ade97",
          "size": 450338,
          "mimetype": "image/jpeg",
          "creation_date": "2020-01-17T17:13:28.131126Z",
          "urls": {
            "source": null,
            "original": "https://fra1.digitaloceanspaces.com/tanukitunes/attachments/9f/47/fb/tmbg.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=d80640f390c9984a942a951c06a28456efafe6136d2dee53b001e551b8836ec4",
            "medium_square_crop": "https://fra1.digitaloceanspaces.com/tanukitunes/__sized__/attachments/9f/47/fb/tmbg-crop-c0-5__0-5-200x200-95.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=a0770c764e2242ee203a71f77be6a3de782050bf46b03683dc883be27c679e65",
            "large_square_crop": "https://fra1.digitaloceanspaces.com/tanukitunes/__sized__/attachments/9f/47/fb/tmbg-crop-c0-5__0-5-600x600-95.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=14d604c022fc2b923e8c124c988a5b855e99f35f8a0bf598e9fe7677096fe990"
          }
        },
        "channel": null
      },
      "release_date": "2007-05-15",
      "cover": {
        "uuid": "8bcc8c7f-0059-4225-ae1e-6472aa918abc",
        "size": null,
        "mimetype": "image/jpeg",
        "creation_date": "2019-11-27T17:08:48.103220Z",
        "urls": {
          "source": null,
          "original": "https://fra1.digitaloceanspaces.com/tanukitunes/albums/covers/2018/12/13/b459dd621-8f47-4af6-97f7-2f925e685853.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=a89794b6a107a1bb39e4e4bf161f895969c37f606ba07aac7cc7b41d2489e376",
          "medium_square_crop": "https://fra1.digitaloceanspaces.com/tanukitunes/__sized__/albums/covers/2018/12/13/b459dd621-8f47-4af6-97f7-2f925e685853-crop-c0-5__0-5-200x200-95.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=f14d528c7305054d702e62cd8f2c62aad7eb0afcf3e2088b0678d012cf8ac44c",
          "large_square_crop": "https://fra1.digitaloceanspaces.com/tanukitunes/__sized__/albums/covers/2018/12/13/b459dd621-8f47-4af6-97f7-2f925e685853-crop-c0-5__0-5-600x600-95.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=CKT5DNTMO5K4DPLYNTIY%2F20231118%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20231118T132814Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=e32aefab24ac6ac7c382d34291d10c9af515c33c85f01f8f059d5d58df8eca9f"
        }
      },
      "creation_date": "2018-12-13T00:17:38.395691Z",
      "is_local": true,
      "tracks_count": 13
    },
    "uploads": [
      {
        "uuid": "d19b0cfe-427d-4f70-8a77-3906e8f7a7a3",
        "listen_url": "/api/v1/listen/fd003ce3-83bd-4231-ab6b-13c59f2e85ab/?upload=d19b0cfe-427d-4f70-8a77-3906e8f7a7a3",
        "size": 3502417,
        "duration": 197,
        "bitrate": 192000,
        "mimetype": "audio/ogg",
        "extension": "ogg",
        "is_local": true
      }
    ],
    "listen_url": "/api/v1/listen/fd003ce3-83bd-4231-ab6b-13c59f2e85ab/",
    "tags": [],
    "attributed_to": null,
    "id": 781,
    "fid": "https://tanukitunes.com/federation/music/tracks/fd003ce3-83bd-4231-ab6b-13c59f2e85ab",
    "mbid": "5724b81c-f32c-4375-9bdc-fce4c87fc4ed",
    "title": "With the Dark",
    "creation_date": "2018-12-13T00:17:53.119857Z",
    "is_local": true,
    "position": 7,
    "disc_number": null,
    "downloads_count": 4,
    "copyright": null,
    "license": null,
    "cover": null,
    "is_playable": true
  },
  "creation_date": "2023-11-17T15:43:46.062258Z",
  "actor": {
    "fid": "https://tanukitunes.com/federation/actors/doctorworm",
    "url": "https://tanukitunes.com/@doctorworm",
    "creation_date": "2018-12-12T22:12:18Z",
    "summary": null,
    "preferred_username": "doctorworm",
    "name": "doctorworm",
    "last_fetch_date": "2022-12-20T15:38:06.651418Z",
    "domain": "tanukitunes.com",
    "type": "Person",
    "manually_approves_followers": false,
    "full_username": "doctorworm@tanukitunes.com",
    "is_local": true
  }
}
```

To avoid this, serializers should follow this pattern:

- Only full serializers should reference other entities
- Only the `Base` serializer for an entity should be referenced

Using this format, the resulting `/api/v2/history/listenings` endpoint would contain the following:

- `Listening` objects containing the following information:
  - The `BaseUser` who recorded the `Listening`
  - The `BaseActor` of the `User`
  - The `BaseRecording` (the recording/track the user listened to) including the associated `ArtistCredit`

In this format, no `Base` serializer ever references another entity. This reduces the complexity of the result while still providing all required information.

```json
{
  "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "createdDate": "2023-11-18T13:58:25.187Z",
  "recording": {
    "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "fid": "string",
    "name": "string",
    "playable": true,
    "local": true,
    "artistCredit": [
      {
        "name": "string",
        "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "joinPhrase": "string"
      }
    ],
    "cover": {
      "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "mimetype": "string",
      "size": 0,
      "creationDate": "2023-11-18T13:58:25.187Z",
      "urls": {
        "source": "string",
        "original": "string"
      }
    }
  },
  "user": {
    "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "string",
    "fullUsername": "string",
    "preferredUsername": "string",
    "avatar": {
      "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "mimetype": "string",
      "size": 0,
      "creationDate": "2023-11-18T13:58:25.187Z",
      "urls": {
        "source": "string",
        "original": "string"
      }
    }
  },
  "actor": {
    "fid": "string",
    "url": "string",
    "fullUsername": "string",
    "preferredUsername": "string",
    "name": "string",
    "domain": "string",
    "local": true
  }
}
```

## Appropriate use of subpaths

Most endpoints in API v1 return large amounts of information and terminate at the collection level or one subpath deeper. API v2 should be designed to split the responsibilities of endpoints into more specific subpath operations.

Entities related to an item such as a collection, artist, release, or recording should be delegated to subpath queries such as `/api/v2/collections/{guid}/artists` rather than relying on filtering large result sets. While this increases the number of calls made by the frontend, it has the following positive impacts:

- The API follows REST conventions more closely
- Each call can be repeated by the frontend at a much lower cost. This can be useful for refreshing content or updating components
- It dramatically decreases the APIs complexity and makes the resulting code much more maintainable

### Case study

In Funkwhale API v1, calling the `/api/v1/artists` endpoint returns a list of `ArtistWithAlbums` objects. These objects contain a huge amount of information, some of which is duplicated.

```json
{
  "count": 123,
  "next": "http://api.example.org/accounts/?page=4",
  "previous": "http://api.example.org/accounts/?page=2",
  "results": [
    {
      "albums": [
        {
          "tracks_count": 0,
          "cover": {
            "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "size": 0,
            "mimetype": "string",
            "creation_date": "2023-11-19T14:07:15.065Z",
            "urls": {
              "additionalProp1": "string",
              "additionalProp2": "string",
              "additionalProp3": "string"
            }
          },
          "is_playable": true,
          "is_local": true,
          "id": 0,
          "fid": "string",
          "mbid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
          "title": "string",
          "artist": 0,
          "release_date": "2023-11-19",
          "creation_date": "2023-11-19T14:07:15.065Z"
        }
      ],
      "tags": ["string"],
      "attributed_to": {
        "fid": "string",
        "url": "string",
        "creation_date": "2023-11-19T14:07:15.065Z",
        "summary": "string",
        "preferred_username": "string",
        "name": "string",
        "last_fetch_date": "2023-11-19T14:07:15.065Z",
        "domain": "string",
        "type": "Person",
        "manually_approves_followers": true,
        "full_username": "string",
        "is_local": true
      },
      "channel": {
        "uuid": "string",
        "actor": {
          "full_username": "string",
          "preferred_username": "string",
          "domain": "string"
        }
      },
      "tracks_count": 0,
      "id": 0,
      "fid": "string",
      "mbid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "string",
      "content_category": "string",
      "creation_date": "2023-11-19T14:07:15.065Z",
      "is_local": true,
      "cover": {
        "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "size": 0,
        "mimetype": "string",
        "creation_date": "2023-11-19T14:07:15.065Z",
        "urls": {
          "additionalProp1": "string",
          "additionalProp2": "string",
          "additionalProp3": "string"
        }
      }
    }
  ]
}
```

While this can be useful for minimizing the number of calls made to the API, it negatively impacts the performance of the endpoint.

To address this, Funkwhale API v2 should split this up into the following endpoints:

- `/api/v2/artists`: returns a list of `BaseArtist` objects

```json
{
  "total": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "fid": "string",
      "mbid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "string",
      "contentCategory": "music",
      "local": true,
      "cover": {
        "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "mimetype": "string",
        "size": 0,
        "creationDate": "2023-11-19T01:22:37.246Z",
        "urls": {
          "source": "string",
          "original": "string"
        }
      },
      "tags": ["string"]
    }
  ]
}
```

- `/api/v2/artists/{guid}`: returns a full `Artist` object

```json
{
  "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "fid": "string",
  "mbid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "string",
  "contentCategory": "music",
  "local": true,
  "cover": {
    "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "mimetype": "string",
    "size": 0,
    "creationDate": "2023-11-19T01:21:28.768Z",
    "urls": {
      "source": "string",
      "original": "string"
    }
  },
  "tags": ["string"],
  "creationDate": "2023-11-19T01:21:28.768Z",
  "recordingCount": 0
}
```

- `/api/v2/artists/{guid}/releases`: returns a list of `BaseRelease` objects accredited to the artist

```json
{
  "total": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "fid": "string",
      "mbid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "string",
      "artistCredit": {
        "name": "string",
        "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "joinPhrase": "string"
      },
      "playable": true,
      "cover": {
        "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "mimetype": "string",
        "size": 0,
        "creationDate": "2023-11-19T01:21:51.779Z",
        "urls": {
          "source": "string",
          "original": "string"
        }
      }
    }
  ]
}
```

- `/api/v2/artists/{guid}/recordings`: returns a list of `BaseRecording` objects accredited to the artist

```json
{
  "total": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "fid": "string",
      "name": "string",
      "playable": true,
      "local": true,
      "artistCredit": [
        {
          "name": "string",
          "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
          "joinPhrase": "string"
        }
      ],
      "cover": {
        "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "mimetype": "string",
        "size": 0,
        "creationDate": "2023-11-19T01:22:37.278Z",
        "urls": {
          "source": "string",
          "original": "string"
        }
      }
    }
  ]
}
```

- `/api/v2/artists/{guid}/collections`: returns a list of `BaseCollections` that contain the artist

```json
{
  "total": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "string",
      "local": true,
      "owner": {
        "fid": "string",
        "fullUsername": "string",
        "preferredUsername": "string",
        "name": "string",
        "domain": "string",
        "local": true
      }
    }
  ]
}
```

This pattern can be repeated for other content types.
