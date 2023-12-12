# ActivityPub overview

## Actors

Funkwhale uses [ActivityPub actors][actor-object] to hold and manage access to content. There are five main types of actor:

Service actor
: The **Service actor** is a special actor that represents a Funkwhale pod. ActivityPub actors can [follow this actor][follow-activity] to receive updates to public content stored on the pod.

User
: A **User** is an actor that represents **either** a person with a Funkwhale account **or** a _virtual_ user that controls access to a **Channel**. _Regular_ **Users** can own Funkwhale **Collection** actors to add content to their [ActivityPub Collection][collections].

: _Regular_ **Users** may follow other **Users** to receive updates about the **User's** _Favorites_ ([likes collection](https://www.w3.org/TR/activitypub/#likes)) and _Listening activity_.

: Multiple _regular_ **Users** can own a _virtual_ **User** to control access to a **Channel**. This is useful in the example of bands or groups who might share access to a joint account. A **User** may authenticate as the _virtual_ user to add content to a **Channel's**
[ActivityPub Collection][collections].

Collection
: A **Collection** is an actor that represents a collection of content owned by a **User**. ActivityPub actors can [follow this actor][follow-activity] to be notified of changes to the collection's content.

Channel
: A **Channel** is an actor that represents a public stream of content owned by a _virtual_ **User**. Funkwhale **Users** with access to the _virtual_ **User** may manage content in the **Channel's** collection. ActivityPub actors can [follow this actor][follow-activity] to be notified of changes to the collection's content.

Each actor must have a globally unique username that identifies them across federation. The `preferredUsername` field should be used to render the actor's name in all representations. Actor owners can change the `preferredUsername` of the actor at any time to update how it is represented.

```{mermaid}
erDiagram
    Pod ||--|| ServiceActor : contains
    Pod ||--|{ Users: contains
    Users ||--|{ Collections : owns
    Users }|--o{ VirtualUsers : accesses
    VirtualUsers ||--|{ Channels : owns
    Users }|--o{ Collections : follows
    Users }|--o{ Channels : follows
    Channels }|--|| ServiceActor : "public content"
    Collections }|--|| ServiceActor : "public content"
    ServiceActor ||--|| Outbox : publish
```

## Service actor outbox

The **Service actor** publishes _public_ Funkwhale content to its [outbox][outbox]. When new content is added to a _public_ **Collection** or to a **Channel**, this update is added to the **Service actor's** outbox. Actors in the [followers collection][followers-collection] receive updates in their [inbox][inbox] and display the new content.

Pods may follow one another's public content by having their **Service actor** follow the target pod's **Service actor**. If the target **Service actor** [accepts][accept-activity] the follow request, the requesting **Service actor** is added to the target **Service actor's** follower collection.

```{mermaid}
sequenceDiagram
    Pod A->>Pod B: Follow
    Pod B-->>Pod A: Accept
    loop New items are added to the outbox
        Pod B->>Pod A: New items
    end
```

**Service actors** publish the following to their outbox:

- Addition of new public content (represented as [created actvities][create-inbox] against content objects)
- Deletion of public content (represented as [delete activities][delete-activity] against content objects)
- Changes to public content details (represented as [update activities][update-activity] against content objects)

```{mermaid}
sequenceDiagram
    User->>Service actor: Add new public content
    Service actor->>Outbox: Create content object
    Outbox->>Follower collection: Create content object
    User->>Service actor: Delete public content
    Service actor->>Outbox: Delete content object
    Outbox->>Follower collection: Delete content object
    User->>Service actor: Update public content
    Service actor->>Outbox: Update content object
    Outbox->>Follower collection: Update content object
```

## Regular user outbox

**Regular** actors publish the following to their [outbox][outbox]:

- Their favorites (represented as liked objects in their [likes collection][likes]
- Their listens (represented as [created activities][create-inbox] against listening objects)

### Favorite action

```{mermaid}
sequenceDiagram
    par
        User->>Funkwhale API: Favorite content
        User->>Outbox: Like content object
    end
    Outbox->>Follower collection: Like content object
```

### Listen action

```{mermaid}
sequenceDiagram
    par
        User->>Funkwhale API: Listen
        User->>Outbox: Create listen object
    end
    Outbox->>Follower collection: Create listen object
```

## Collection outbox

**Collection** actors publish the following to their [outbox][outbox]:

- Addition of new content (represented as [created activities][create-inbox] against content objects)
- Deletion of content (represented as [delete activities][delete-activity] against content objects)
- Changes to content details (represented as [update activities][update-activity] against content objects)

```{mermaid}
sequenceDiagram
    User->>Collection: Add new content
    Collection->>Outbox: Create content object
    Outbox->>Follower collection: Create content object
    User->>Collection: Delete content
    Collection->>Outbox: Delete content object
    Outbox->>Follower collection: Delete content object
    User->>Collection: Update content
    Collection->>Outbox: Update content object
    Outbox->>Follower collection: Update content object
```

## Channel outbox

**Channel** actors publish the following to their [outbox][outbox]:

- Addition of new content (represented as [created actvities][create-inbox] against content objects)
- Deletion of content (represented as [delete activities][delete-activity] against content objects)
- Changes to content details (represented as [update activities][update-activity] against content objects)

```{mermaid}
sequenceDiagram
    User->>Channel: Add new content
    Channel->>Outbox: Create content object
    Outbox->>Follower collection: Create content object
    User->>Channel: Delete content
    Channel->>Outbox: Delete content object
    Outbox->>Follower collection: Delete content object
    User->>Channel: Update content
    Channel->>Outbox: Update content object
    Outbox->>Follower collection: Update content object
```

[actor-object]: https://www.w3.org/TR/activitypub/#actor-objects
[inbox]: https://www.w3.org/TR/activitypub/#inbox
[outbox]: https://www.w3.org/TR/activitypub/#outbox
[collections]: https://www.w3.org/TR/activitypub/#collections
[followers-collection]: https://www.w3.org/TR/activitypub/#followers
[create-inbox]: https://www.w3.org/TR/activitypub/#create-activity-inbox
[likes]: https://www.w3.org/TR/activitypub/#likes
[delete-activity]: https://www.w3.org/TR/activitypub/#delete-activity-inbox
[update-activity]: https://www.w3.org/TR/activitypub/#update-activity-inbox
[accept-activity]: https://www.w3.org/TR/activitypub/#accept-activity-inbox
[follow-activity]: https://www.w3.org/TR/activitypub/#follow-activity-outbox
