Favorite and listenings sync with listenbrainz
===

## The issue

This is a new feature allowing better recommendations and radios. Also Troi need some local data to resolve avoid server load on listenbrainz side. 

## Proposed solution

Sync favorite and listenings with listenbrainz to get better recommendations and to filter out recently listened tracks from radios.

## Feature behavior

We will query listenings and favorites from Listenbrainz and add the related attributes to funkwhale tables. 

### Backend
Use the listenbrainz funkwhale plugin to handle this. 

- Update the `TrackFavorite` and `Listening` models with a new boolean attribute : `from_listenbrainz`
Api endpoints can be found here : https://listenbrainz.readthedocs.io/en/latest/users/api/core.html

- A task to sync listenings and favorites daily. 
- A special care has to be made to avoid listenings duplicates in case the user scrobble listening from funkwhale to musicbrainz. We can use the `submission_client` attribute of lb listenning and exclude the one coming from "Funkwhale ListenBrainz plugin"

### Frontend

In the Listenbrainz pluging add: 
- User setting to set the listenbrainz User token
- User setting to choose if favorite sync will be from fw to lb, from lb to fw or both side
- USer setting to enable Listenbrainz listening syncc

## Availability

- [ ] Admin panel
- [x] App frontend
- [ ] CLI

## Responsible parties


## Open questions


## Minimum viable product

### Next steps
