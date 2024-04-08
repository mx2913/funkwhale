from config import plugins

PLUGIN = plugins.get_plugin_config(
    name="listenbrainz",
    label="ListenBrainz",
    description="A plugin that allows you to submit or sync your listens and favorites to ListenBrainz.",
    homepage="https://docs.funkwhale.audio/users/builtinplugins.html#listenbrainz-plugin",  # noqa
    version="0.3",
    user=True,
    conf=[
        {
            "name": "user_token",
            "type": "text",
            "label": "Your ListenBrainz user token",
            "help": "You can find your user token in your ListenBrainz profile at https://listenbrainz.org/profile/",
        },
        {
            "name": "user_name",
            "type": "text",
            "required": False,
            "label": "Your ListenBrainz user name.",
            "help": "Required for importing listenings and favorites with ListenBrainz \
                but not to send activities",
        },
        {
            "name": "submit_listenings",
            "type": "boolean",
            "default": True,
            "label": "Enable listening submission to ListenBrainz",
            "help": "If enabled, your listenings from Funkwhale will be imported into ListenBrainz.",
        },
        {
            "name": "sync_listenings",
            "type": "boolean",
            "default": False,
            "label": "Enable listenings sync",
            "help": "If enabled, your listening from ListenBrainz will be imported into Funkwhale. This means they \
                will be used along with Funkwhale listenings to filter out recently listened content or \
                generate recommendations",
        },
        {
            "name": "sync_favorites",
            "type": "boolean",
            "default": False,
            "label": "Enable favorite sync",
            "help": "If enabled, your favorites from ListenBrainz will be imported into Funkwhale. This means they \
                will be used along with Funkwhale favorites (UI display, federation activity)",
        },
        {
            "name": "submit_favorites",
            "type": "boolean",
            "default": False,
            "label": "Enable favorite submission to ListenBrainz services",
            "help": "If enabled, your favorites from Funkwhale will be submitted to ListenBrainz",
        },
    ],
)
