# User deletion spec

## Terminology

The following terminology is used throughout this document:

User
: A **person** with an account on a Funkwhale server or ActivityPub-enabled platform.

Object
: A collection of information - formatted as [`JSON-LD`](https://json-ld.org/) - that represents entities such as content, users, or activities performed in Funkwhale. See the [ActivityPub specification](https://www.w3.org/TR/activitypub/#obj) for more details.

Activity
: A verb that describes an action targeting an **Object**. This informs the receiving server what it needs to do with the object. For example: `Create`, `Delete`, `Undo`, `Follow`, `Block`.

Actor
: An ActivityPub object acting on behalf of another object across federated services. See the [ActivityPub specification][actor] for more details.

Tombstone
: A status that marks an object as deleted but leaves some metadata intact to prevent reuse.

## The issue

Funkwhale users broadcast activities such as Listenings and Favorites both locally and over federation. Users require the ability to fully delete their presence from local and federated servers to comply with their request.

## The solution

User deletions must be actioned as _cascading_ deletions both locally and across federation. Any action associated with a user's actor should be deleted, and the actor itself must be marked as `Tombstoned` to prevent another user from claiming the actor in future.

When a user deletes their account, the following must happen:

1. The local server must remove all Favorites, Listenings, Collections, and Uploads owned by the actor

:::{info}
If the user owns any joint Channels or Playlists, these should only be deleted if the user is the **only** user with access to the object.
:::

3. The local server must delete the user's actor and mark it as `Tombstoned`
4. The local server must delete the actor of any Channels owned solely by the user and mark them as `Tombstoned`
5. The local server's **Service actor** must broadcast the deletion to the **Service actors** of all servers known to it
6. Remote servers should delete all data associated with the deleted actor, including cached content belonging to the actor

```{mermaid}
sequenceDiagram
    User ->> API : Delete account
    API -->> User : Acknowledge
    par cascade deletion in the background
        API ->> Database : Cascade delete local content
        activate Database
        API ->> Service actor : Broadcast deletion
        Service actor ->> Remote servers : Broadcast deletion
        Remote servers -->> Service actor : Cascade delete
    end
```

### API behavior

The Funkwhale client API is responsible for handling deletion requests and actioning the resulting cascade deletion. Users should request a deletion using a `DELETE` request:

```http
DELETE /api/v2/users/{id}
```

:::{danger}
Users must only be able to delete their own account. Unauthorized deletion requests must return a `401: Unauthorized` response.

Admins and moderators with sufficient privilege to remove accounts should be able to remove local accounts using this endpoint.
:::

On receipt of a deletion request, the API must return a `202: Accepted` response to inform the user that the deletion process has been received.

If the server admin has enabled email notifications, the server should send an email notifying the user that their account has been successfully started and all of their information will be deleted.

After this, the server must handle the following:

1. Deleting any Uploads owned by the user
2. Deleting any Favorites associated with the user
3. Deleting any Listenings associated with the actor
4. Deleting any Playlists associated with the actor
5. Deleting any Collections owned by the user
6. Deleting any Channels owned solely by the user

The user's account information (such as name, email address, signup date, last login) must be removed and their federation actor `Tombstoned` to prevent reuse of their handle. Since Channels and Collections are federation actors with their own collection of followers, these must also be `Tombstoned` and their identifying information removed.

If a request is sent to the API for a `Tombstoned` actor, it must respond with `410: Gone`.

### ActivityPub behavior

Funkwhale must broadcast any deletion requests to ActivityPub servers with which it has previously interacted by posting a [`Delete` activity][delete] targeting the user's [actor] to the Service Actor's [outbox]. The Service actor should broadcast the following:

1. A [`Delete` activity][delete] for the user's [actor]
2. A [`Delete` activity][delete] for the actor of any Collections owned by the user
3. A [`Delete` activity][delete] for the actor of any Channels owned solely by the user
4. A [`Delete` activity][delete] for the actor of any Channel owner owned solely by the user

```{mermaid}
flowchart TD
    delete([The user sends a DELETE request]) --> outbox(The deletion is added to\nthe Service actor's outbox)
    outbox --> collections{Does the user own\nany collections?}
    collections -->|yes| tscollection(The collection is tombstoned and the deletion\nis added to the Service actor's outbox)
    tscollection --> virtual{Does the user solely own any\nvirtual actors?}
    virtual -->|yes| tsvirtual(The virtual actor is tombstoned and the deletion\nis added to the Service actor's outbox)
    tsvirtual --> channel{Does the virtual actor own any\nChannels?}
    channel -->|yes| tschannel(The Channel is tombstoned and the deletion\nis added to the Service actor's outbox)
    outbox & tscollection & tsvirtual & tschannel --> serviceactor([The Service actor broadcasts\nall deletions to known servers])
```

On receipt of a [`Delete` activity][delete], the server should cascade delete any content owned by the targeted actor.

### Web app behavior

The Funkwhale web app must present users with a dangerous button to action an account deletion request. This button must be prefaced with clear prose that outlines precisely the impact that deleting an account has.

To ensure that users don't delete their account by mistake, they must verify their request twice and input their password to prevent abuse of the feature. The user experience flow for deleting an account goes as follows:

1. The user navigates to their account settings page
2. The user locates the "Delete account" button that is clearly and visually separated from other actions on the page
3. The user reads the warnings about the deletion process and selects the button to begin the deletion process
4. A modal appears asking the user to authenticate by typing in the name of the targeted object (for example: their username)
5. If the object name is entered correctly, the user is presented with a final warning that informs them that the deletion process can't be reversed
6. If the user chooses to proceed, the app logs the user out and informs them that the deletion process has begun

```{mermaid}
flowchart TD
    settings([The user navigates to\nthe settings menu]) --> delete(The user selects the\nDelete account button)
    delete --> password(A password input appears)
    password --> correctpass{Did the user enter their\npassword correctly?}
    correctpass -->|yes| warning(A final warning appears informing\nthe user that the deletion process\nis destructive and irreversible)
    warning --> confirm{Did the user confirm the\naccount deletion?}
    confirm -->|yes| logout(The user is logged out and a notification\nconfirms their account is gone)
    logout --> email([The server sends the user an email to\nconfirm the deletion])
    correctpass & confirm -->|no| cancel([The account deletion process is\ncancelled])
```

## Availability

- [x] App frontend
- [x] CLI

## Responsible parties

The following working groups are responsible for implementing this feature:

- The **Backend group** is responsible for building the API endpoints and ActivityPub S2S logic
- The **Frontend group** is responsible for creating the interface for in-app account deletion using Funkwhale UI components
- The **Documentation group** is responsible for finalizing the specification of the feature and documenting it for users

## Minimum viable product

The MVP for this feature is to implement the backend logic to enable Funkwhale users to fully delete their accounts and their content. Since users don't currently share content over ActivityPub, only local deletion needs to be achieved for the MVP.

Since **Channels** currently implement ActivityPub behavior, we need to confirm that:

- Channel deletions broadcast the object deletion to remote servers
- Remote servers remove all associated data when a deletion broadcast is received

### Next steps

At each stage of development, we need to consider how account deletion factors into features. Each ActivityPub-enabled feature must have deletion logic as part of its structure.

[outbox]: https://www.w3.org/TR/activitypub/#outbox
[actor]: https://www.w3.org/TR/activitypub/#actors
[delete]: https://www.w3.org/TR/activitypub/#delete-activity-outbox
