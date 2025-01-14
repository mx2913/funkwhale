# Upload process

## The issue

Our current upload process is quite cumbersome and can be confusing for new users. Essentially, users have to know exactly where they want to put content before they've even uploaded it, and once it's uploaded it's hard to move.

There are currently 2 upload flows:

### Upload to library

Uploading to a content library is the oldest upload mechanism in Funkwhale. The flow goes like this:

1. The user clicks on the upload button
2. The user selects "Upload third-party content in a library"
3. The user chooses which library they want to upload to and clicks "Upload"
4. The user selects content or drags and drops it to complete the upload

### Upload to a channel

Channels are a newer feature, but the upload process is largely the same:

1. The user clicks on the upload button
2. The user selects "Publish your work in a channel"
3. The user selects the channel they want to upload to
4. The user selects "Upload"
5. The user enters some metadata about the entry
6. The user selects content or drags and drops it to complete the upload
7. The user inputs relevant details about each track

## Proposed solution

To simplify this flow, the upload process should have a single entrypoint which then guides the user to the correct upload context. Rather than needing to go through a series of steps to upload each item. The proposed solution is to create a single modal for uploads that doesn't require the user to navigate to upload content to different locations.

## Feature behavior

The new feature will present an upload menu that gives users all upload options as a selectable radio menu:

1. Library (later Collections)
2. Music channel
3. Podcast channel

Once the user selects an option, they can select the target from a dropdown and start uploading straight away.

### Frontend

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
7. Funkwhale assesses if all files have the correct metadata and highlights any issues for the user to fix _with a meaningful message_. The frontend keep the connection open until the API sends a response

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
   process --> message([Funkwhale returns status messages for all uploads\nand notifies the user the the upload is complete])
```

The frontend should reflect the **status** of the upload to inform the user how the upload is progressing:

- `Failed`: The file is improperly tagged **or** the API has responded with an error
- `Uploading`: The file is being sent to the server
- `Processing`: The server is processing the file and no success response has been returned yet
- `Success`: The API has responded with a `200: Success` response and passed back information about the upload.

#### UX considerations

To prevent disrupted uploads, the following UX should be implemented

- If the user dismisses the modal with the escape key, by clicking outside the modal, or by moving back to the previous page, _the user should be warned and given the option to cancel their upload or continue it in the background_
- The user should have the option to cancel an upload at any time
- If an upload is sent to the background, it should notify the user in some way when the upload is complete

:::{seealso}
See the [interactive prototype](https://design.funkwhale.audio/#/view/e3a187f0-0f5e-11ed-adb9-fff9e854a67c?page-id=d9f9f4d0-1a7b-11ed-8551-a35b3c702efa&section=interactions&index=0) for an overview of the behavior.
:::

### Backend behavior

The upload process remains the same on the backend. However, the error checking needs to be more descriptive. For example:

- Failed metadata checks should be explicit about what issues were found in the metadata and should return this in a readable way for the user to fix
- If an upload fails partway, this should be made clear so that the user can attempt a reupload
- The backend should return a meaningful status message reflecting the file processing state

#### Response structure (V2 only)

If the upload succeeds, the API should respond with a `200: Success` message and return a payload containing the following information:

- The upload `guid`
- The `title` of the uploaded file
- The `createdDate` of the upload
- The `fileType` of the upload
- The associated `recording`
- The associated `release`
- The `owner` (actor) of the upload

```json
{
  "guid": "18c455d8-9840-4000-804d-c53e92d85d01",
  "title": "string",
  "createdDate": "1970-01-01T00:00:00.000Z",
  "fileType": "flac",
  "recording": {
    "guid": "18c455d8-9840-4000-82af-67024a9e2018",
    "fid": "http://example.com",
    "name": "string",
    "playable": false,
    "local": false,
    "artistCredit": [
      {
        "name": "string",
        "guid": "18c455d8-9840-4000-8271-2731b97a2c01",
        "mbid": "18c455d8-9840-4000-8f04-1f9dd7f16201",
        "joinPhrase": "string"
      }
    ],
    "cover": {
      "guid": "18c455d8-9840-4000-85af-4178e969db01",
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
    "guid": "18c455d8-9840-4000-81e9-3cc3a7567201",
    "fid": "http://example.com",
    "mbid": "18c455d8-9840-4000-8b86-dd1e40a7bb80",
    "name": "string",
    "artistCredit": [
      {
        "name": "string",
        "guid": "18c455d8-9840-4000-88dc-fd4cf3957201",
        "mbid": "18c455d8-9840-4000-8e40-35019dd11180",
        "joinPhrase": "string"
      }
    ],
    "playable": false,
    "cover": {
      "guid": "18c455d8-9840-4000-831e-ea8add02c380",
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
