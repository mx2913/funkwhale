## Playlist Federation

### The Issue

Playlists are a useful way to curate content and share curated lists of tracks. Currently, only local playlists are browsable in the pods, and a user cannot add a playlist to their library.

### Proposed Solution

Make playlists a federated object to allow them to be added to remote libraries/pods. Send playlist updates throw federation activities. 

### Feature Behavior

Users will be able to click on a "Follow playlist" button. The playlist content and the playlist itself will be added to the user's library section.

#### Backend

Adding a playlist to a library is an ActivityPub `Follow`. The follow request is made to an actor specially created for the playlist. For better understandability, this actor should be named after the playlist name and the user actor owning the playlist. For example, if John has a "Rock" playlist, the actor should be called: john_rock_playlist.

Endpoints should follow the existing federation endpoints.

Add playlist update activities to notifications. 

#### Frontend

- Add a "Follow" button that will call an ActivityPub follow request on the playlist actor.

### Availability

- [ ] Admin panel
- [x] App frontend
- [ ] CLI

### Open Questions

- Frontend design: There isn't any space for followed content in the UI (either for user or playlist follow). A dedicated page should be created.

### Minimum Viable Product

### Next Steps
