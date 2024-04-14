# Glossary of terms

## Funkwhale glossary

{.glossary}
Pod
: A pod is an instance of Funkwhale running on a server. Pods can communicate with one another across the {term}`Fediverse`.

Authenticated
: Users who have an account on a Funkwhale pod. These users provide their authentication information when accessing content.

Anonymous
: Users who do not have an account on a Funkwhale pod. These users don't provide any authentication when accessing content.

Permissions
: Additional rights that an administrator/moderator can grant to a user. Permissions grant access to menus and actions in Funkwhale.

Available permissions:

- {guilabel}`Moderation` – Grants access to the {guilabel}`Moderation` menu. Enables the user to moderate users, domains, and the allow-list.
- {guilabel}`Manage library` – Grants access to the {guilabel}`Library` menu. Enables the user to make changes to library content. This includes deleting local objects and handling edit suggestions.
- {guilabel}`Manage instance-level settings` – Grants access to the {guilabel}`Settings` menu. Enables the user to make changes to pod-level settings such as security settings and API behavior.

{.glossary}
Report categories
: The different types of report a person can submit to your pod.

Available categories:

- {guilabel}`Takedown request` – allow users to request content be removed from your pod.
- {guilabel}`Invalid metadata` – allow users to inform moderators about incorrect metadata on content.
- {guilabel}`Illegal content` – allow users to flag content as illegal.
- {guilabel}`Offensive content` – allow users to flag offensive or hurtful content to moderators.
- {guilabel}`Other` – allow users to submit reports that don't fit into the above categories.

## Channel glossary

{.glossary}
Fediverse
: A term used to refer to a collection of federated (interconnected) servers. These servers run software that enables users to publish and host their own content.

Podcatcher
: A podcatcher is a piece of software that can read podcast feeds. Podcatchers enable listeners to follow and listen to podcast content.

## Plugin glossary

{.glossary}
Plugin
: A plugin is a piece of software that extends the functionality of another piece of software.

Scrobbling
: Scrobbling is the act of recording listen data. Services use this information to keep track of listening preferences and recommend music.

## ActivityPub glossary

{.glossary}
User
: A **person** with an account on a Funkwhale server or ActivityPub-enabled platform.

Object
: A collection of information - formatted as [`JSON-LD`](https://json-ld.org/) - that represents entities such as content, users, or activities performed in Funkwhale. See the [ActivityPub specification](https://www.w3.org/TR/activitypub/#obj) for more details.

Activity
: A verb that describes an action targeting an **Object**. This informs the receiving server what it needs to do with the object. For example: `Create`, `Delete`, `Undo`, `Follow`, `Block`.

Actor
: An ActivityPub object acting on behalf of another object across federated services. See the [ActivityPub specification](https://www.w3.org/TR/activitypub/#actors) for more details.

Service actor
: A special actor that represents a Funkwhale pod. ActivityPub actors can [follow this actor](https://www.w3.org/TR/activitypub/#follow-activity-outbox) to receive updates to public content stored on the pod.

Tombstone
: A status that marks an object as deleted but leaves some metadata intact to prevent reuse.
