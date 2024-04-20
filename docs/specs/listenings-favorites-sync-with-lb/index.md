Favorite and listenings sync with listenbrainz
===

## The issue

Currently, Funkwhale listens and favorites are useful only within the Funkwhale ecosystem. There is no way to import historical listens/favorites from other services, nor to communicate listens and favorites with external services to keep listening aligned across platforms.



## Proposed solution

This is a new feature that allows users to sync listening and favorites with ListenBrainz. It can be used to import liked and listened content from other services (YouTube, Deezer, etc) into Funkwhale. Additionally, it enables Troi to utilize local data instead of making queries to ListenBrainz servers, reducing the load on their side and improving performance in recommendation generation.

## Feature behavior

The synchronization of content will behave as follows:

- Funkwhale pulls new litenings from ListenBrainz on a daily basis for active users
- The ListenBrainz plugin sends new listens and favorites to ListenBrainz when the user performs the corresponding action in Funkwhale


### Backend
To facilitate syncing of data between Funkwhale and MusicBrainz, we need to update the ListenBrainz plugin to send favorites. We also need to create tasks to retrieve listenings and favorites from ListenBrainz.

To keep track of where a favorite or listen occurred, we need to extend our data models to account for external sources. To do this, the following actions are needed:

1. The `TrackFavorite` and `Listening` models need a new string attribute: `source`
2. The ListenBrainz plugin must set the `source` attribute to `listenbrainz` when it creates new favorites and listens

On the server side, we require a new daily task to pull listenings and favorites directly from ListenBrainz. To avoid duplicated data, we should discount any ListenBrainz results that have

- the same timestamp as a matching Funkwhale action
- the following attribute: `submission_client: "Funkwhale ListenBrainz plugin"`

### Frontend

Add the following options to the ListenBrainz plugin
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
