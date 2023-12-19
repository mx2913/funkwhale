Favorite and listenings sync with listenbrainz
===

## The issue

This is a new feature that allows users to sync listening and favorites with ListenBrainz. It can be used to import liked and listened content from other services (YouTube, Deezer, etc) into Funkwhale. Additionally, it enables Troi to utilize local data instead of making queries to ListenBrainz servers, reducing the load on their side and improving performance in recommendation generation.

## Proposed solution

Update the Listenbrainz plugin to send likes to listenbrainz. Add tasks to get listenings and favorites from Listenbrainz

## Feature behavior

Pulling will happen dayly for active users. 
Pushing will happen each time a track is listened or favored. 

### Backend
Use the listenbrainz funkwhale plugin to handle this. 

- Update the `TrackFavorite` and `Listening` models with a new boolean attribute : `source`. 
- When `TrackFavorite` or `Listening` is created from the plugin `source` is set to `Listenbrainz`

- A task to pull listenings and favorites daily. 
- A special care has to be made to avoid listenings duplicates in case the user scrobble listening from funkwhale to musicbrainz. We can use the `submission_client` attribute of lb listenning and exclude the one coming from "Funkwhale ListenBrainz plugin" and than have the same timestamp. 

### Frontend

In the Listenbrainz pluging add: 
- User setting to set the listenbrainz User token
- Push listens
- Pull listens
- Push favorites
- Pull favorites

## Availability

- [ ] Admin panel
- [x] App frontend
- [ ] CLI

## Responsible parties


## Open questions


## Minimum viable product

### Next steps
