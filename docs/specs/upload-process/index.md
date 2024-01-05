# Upload process

## The issue

Funkwhale's current upload process is cumbersome and can be confusing for new users. Essentially, users have to know exactly where they want to put content before they've even uploaded it, and once it's uploaded it's hard to move.

There are currently 2 upload flows:

:::{dropdown} Upload to library

Uploading to a content library is the oldest upload mechanism in Funkwhale. The flow goes like this:

1. The user clicks on the upload button
2. The user selects "Upload third-party content in a library"
3. The user chooses which library they want to upload to and clicks "Upload"
4. The user selects content or drags and drops it to complete the upload

:::

:::{dropdown} Upload to a channel

Channels are a newer feature, but the upload process is similar:

1. The user clicks on the upload button
2. The user selects "Publish your work in a channel"
3. The user selects the channel they want to upload to
4. The user selects "Upload"
5. The user enters some metadata about the entry
6. The user selects content or drags and drops it to complete the upload
7. The user inputs relevant details about each track

:::

## Proposed solution

To simplify this flow, the upload process should have a single entrypoint which then guides the user to the correct upload context. Rather than needing to go through a series of steps to upload each item. The proposed solution is to create a single modal for uploads that doesn't require the user to navigate to upload content to different locations.

## Feature behavior

The new feature will present an upload menu that gives users all upload options as a selectable radio menu:

1. Library (later Collections)
2. Music channel
3. Podcast channel

Once the user selects an option, they can select the target from a dropdown and start uploading straight away.

## Web app

The new workflow goes as follows:

1. The user selects the upload button. An upload modal opens
2. The user selects their upload target:
   - Their music library/collections(s)
   - A music channel
   - A podcast channel
3. The modal displays all items in a selected category as a dropdown list. For example:
   - A list of libraries/collections owned by the user
   - A list of music channels owned by the user
   - A list of podcast channels owned by the user
4. The user selects the location to which they want to upload their content
5. The user selects the files they want to upload from a file picker, or by dragging and dropping files onto the modal
6. The user can select a "Upload in background" button which dismisses the modal but _continues the upload_
7. Funkwhale assesses if all files have the correct metadata and highlights any issues for the user to fix _with a meaningful message_. The web app keep the connection open until the API sends a response

```{mermaid}
flowchart TD
   upload([User selects the upload button]) --> modal(An upload modal opens)
   modal --> select{The user selects their upload target}
   select --> |Library/Collection| library(The modal displays a list of libraries/collections)
   select --> |Music channel| music(The modal displays the user's music channels)
   select --> |Podcast channel| podcast(The modal displays the user's podcast channels)
   library & music & podcast --> choose(The user chooses the upload location)
   choose --> files[The user drags files to upload\nor selects files in a file picker]
   files --> wait(The user waits for the upload to complete) & close(The user closes the modal)
   wait & close --> process(Funkwhale processes the uploads\nand verifies metadata)
   process --> message([Funkwhale returns status messages for all uploads\nand notifies the user the upload is complete])
```

The web app should reflect the **status** of the upload to inform the user how the upload is progressing:

- `Failed`: The file is improperly tagged **or** the API has responded with an error
- `Uploading`: The web app is uploading the file to the server
- `Processing`: The server is processing the file and hasn't returned a response
- `Success`: The API has responded with a `200: Success` response and passed back information about the upload.

### UX considerations

To prevent disrupted uploads, we should implement the following UX:

- If the user dismisses the modal with the escape key, by clicking outside the modal, or by moving back to the previous page, _the web app must warn the user and given the option to cancel their upload or continue it in the background_
- The user should have the option to cancel an upload at any time
- If the user sends the upload modal to the background, Funkwhale should notify the user when the upload is complete

:::{seealso}
See the [interactive prototype](https://design.funkwhale.audio/#/view/e3a187f0-0f5e-11ed-adb9-fff9e854a67c?page-id=d9f9f4d0-1a7b-11ed-8551-a35b3c702efa&section=interactions&index=0) for an overview of the behavior.
:::

## Backend

To give upload results more structure, each upload created in the web app must belong to an upload group. An upload group is a simple collection of uploads.

```{mermaid}
sequenceDiagram
  Client->>+API: POST /api/v2/upload-groups
  API-->>Client: 201 GUID
  loop For each file
    Client->>API: POST /api/v2/upload-groups/{guid}/uploads
    API-->>Client: 200 Creation message
  end
```

### Upload group creation

Authenticated users may create upload groups by sending a POST request to the `/api/v2/upload-groups` endpoint with no request body.

```console
$ curl -X POST "/api/v2/upload-groups" \
 -H "accept: application/json"
```

The user may optionally send a group `name` in the body of the request to give the release group a meaningful name.

```console
$ curl -X POST "/api/v2/upload-groups" \
  -H "Content-type: application/json" \
  -d '{
  "name": "My cool group"
}'
```

:::{note}
If no `name` is present, the server should use the timestamp of the request as the upload group's `name`.
:::

The API should respond with the following information:

- A `201: Created` response
- The `name` of the newly created upload group
- The `guid` of the newly created upload group
- The `uploadUrl` where clients can send new uploads or query the uploads in the group

```json
{
  "status": "201",
  "name": "My cool group",
  "guid": "18c697b6-f0b0-4000-84cd-30e3e4b1a201",
  "uploadUrl": "/api/v2/upload-groups/18c697b6-f0b0-4000-84cd-30e3e4b1a201/uploads"
}
```

Clients should also be able to send a PATCH request to alter the `name` of an upload group:

```console
$ curl -X PATCH "/api/v2/upload-groups/18c697b6-f0b0-4000-84cd-30e3e4b1a201"" \
  -H "Content-type: application/json" \
  -d '{
  "name": "My cool group"
}'
```

The server should respond with a `200: OK` response to reflect that the request updated the resource.

```json
{
  "status": "200",
  "name": "My cool group",
  "guid": "18c697b6-f0b0-4000-84cd-30e3e4b1a201",
  "uploadUrl": "/api/v2/upload-groups/18c697b6-f0b0-4000-84cd-30e3e4b1a201/uploads"
}
```

### File upload

Once the server creates the upload group, the client can send files to the `/api/v2/upload-groups/{guid}/uploads` endpoint to add new uploads to the group.

This endpoint must support 2 methods controlled by the `Content-Type` header:

1. A single file as an `octet-stream`
   - If the client sends an audio file as an `octet-stream`, the server is responsible for parsing the file metadata and managing the import
2. A `multipart/form-data` submission including metadata, the audio file, and an optional cover. This method enables the client to set parse and set metadata information independent of the server

If the client sends a `multipart/form-data` submission, the payload must contain:

- A `metadata` object containing **at least**
  - The `title` of the uploaded file
  - The `artist.name` of the artist
- An optional `target` object containing _any of the following_:
  - An array of collections
  - An array of channels
  - A library
- The audio file

:::{important}
If the client doesn't specify a `target`, the server must implicitly add the upload to the built-in `Uploads` collection.
:::

```console
$ curl -X 'POST' \
  '/api/v2/upload-groups/18c697b6-f0b0-4000-84cd-30e3e4b1a201/uploads' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'metadata={"title": "Juggernaut", \
  "mbid": "3fa85f64-5717-4562-b3fc-2c963f66afa6", \
  "tags": ["Rock"], \
  "position": 1, \
  "entryNumber": 1, \
  "releaseDate": "2023-12-14", \
  "license": "string", \
  "release": {"title": "Juggernaut", "artist": "Autoheart", "mbid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}, \
  "artist": {"name": "Autoheart","mbid": "3fa85f64-5717-4562-b3fc-2c963f66afa6"} \
}' \
  -F 'target={"collections": ["18cda279-b570-4000-800d-580fc7ecb401"]}' \
  -F 'audioFile=@Autoheart - Juggernaut.opus;type=audio/opus' \
  -F 'cover=@cover.png;type=image/png'
```

#### Response structure

If the upload succeeds, the API should respond with a `200: Success` message and return a payload containing the following information:

- The upload `guid`
- The `title` of the uploaded file
- The `createdDate` of the upload
- The `fileType` of the upload
- The `target` of the upload
- The associated `recording`
- The associated `release`
- The `owner` (actor) of the upload

```json
{
  "guid": "18cda279-b5a0-4000-89fc-811321642380",
  "title": "string",
  "createdDate": "1970-01-01T00:00:00.000Z",
  "fileType": "flac",
  "uploadGroup": "18cda279-b5a0-4000-8f5b-fa6702365101",
  "status": "Succeeded",
  "target": {
    "collections": ["18cda279-b5a0-4000-8d96-e9c3c9045c01"]
  },
  "recording": {
    "guid": "18cda279-b5a0-4000-889e-8f6a6a54f401",
    "fid": "http://example.com",
    "name": "string",
    "playable": false,
    "local": false,
    "artistCredit": [
      {
        "name": "string",
        "guid": "18cda279-b5a0-4000-88b1-d3f39c359101",
        "mbid": "18cda279-b5a0-4000-89ff-4e4993cadd01",
        "joinPhrase": "string"
      }
    ],
    "cover": {
      "guid": "18cda279-b5a0-4000-83c2-afe780820380",
      "mimetype": "string",
      "size": 0,
      "creationDate": "1970-01-01T00:00:00.000Z",
      "urls": {
        "source": "http://example.com",
        "original": "http://example.com"
      }
    }
  },
  "release": {
    "guid": "18cda279-b5a0-4000-8e2c-622921d05d01",
    "fid": "http://example.com",
    "mbid": "18cda279-b5a0-4000-868d-ee9479980d80",
    "name": "string",
    "artistCredit": [
      {
        "name": "string",
        "guid": "18cda279-b5a0-4000-8492-68d322f50701",
        "mbid": "18cda279-b5a0-4000-8bc1-f4454eecf980",
        "joinPhrase": "string"
      }
    ],
    "playable": false,
    "cover": {
      "guid": "18cda279-b5a0-4000-85d3-596516082580",
      "mimetype": "string",
      "size": 0,
      "creationDate": "1970-01-01T00:00:00.000Z",
      "urls": {
        "source": "http://example.com",
        "original": "http://example.com"
      }
    }
  },
  "owner": {
    "fid": "http://example.com",
    "fullUsername": "string",
    "preferredUsername": "string",
    "name": "string",
    "domain": "string",
    "local": false
  }
}
```

## Availability

- [ ] Admin panel
- [x] App frontend
- [ ] CLI

## Responsible parties

- **Design group**: mockups and interface designs
- **Frontend group**: building the UI to the design spec
- **Backend group**: develop metadata checks

## Minimum viable product

The MVP for this product should be able to replicate the functionality of the current v1 upload process with the improved workflow outlined above.
