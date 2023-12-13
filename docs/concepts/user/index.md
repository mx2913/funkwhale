# User

In Funkwhale, a **User** represents a **person** who uses the Funkwhale software.

When a person signs up to a Funkwhale server, they create a user profile. This user profile is associated with all of that person's activities, such as:

- Uploading content
- Listening to content
- Favoriting content
- Editing metadata
- Reporting issues

## Web app behavior

Funkwhale shows users a **Profile** which contains the information they have shared on the platform, including a summary of their activities and their content. Users may update this profile information at any time.

Users may follow other users by navigating to their profile and sending a follow request. Following another user displays their shared activity on their profile as well as in activity streams on Funkwhale, such as the "Recently listened" and "Recently favorited" streams.

## Federation behavior

Funkwhale users are represented by [ActivityPub `Actor` objects][actor].

```json-ld
{
  "@context": ["https://www.w3.org/ns/activitystreams",
               {"@language": "en"}],
  "type": "Person",
  "id": "https://open.audio/@betterraves",
  "following": "https://open.audio/@betterraves/following.json",
  "followers": "https://open.audio/@betterraves/followers.json",
  "liked": "https://open.audio/@betterraves/liked.json",
  "inbox": "https://open.audio/@betterraves/inbox.json",
  "outbox": "https://open.audio/@betterraves/feed.json",
  "preferredUsername": "betterraves",
  "name": "Amélie",
  "summary": "A hip-hop artist from Belgium",
  "icon": [
    "https://open.audio/media/__sized__/betterraves.png"
  ]
}
```

[actor]: https://www.w3.org/TR/activitypub/#actor-objects
