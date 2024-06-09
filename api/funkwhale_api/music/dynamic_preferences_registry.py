from django.forms import widgets
from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

music = types.Section("music")


@global_preferences_registry.register
class MaxTracks(types.BooleanPreference):
    show_in_api = True
    section = music
    name = "transcoding_enabled"
    verbose_name = "Transcoding enabled"
    help_text = (
        "Enable transcoding of audio files in formats requested by the client. "
        "This is especially useful for devices that do not support formats "
        "such as Flac or Ogg, but the transcoding process will increase the "
        "load on the server."
    )
    default = True


@global_preferences_registry.register
class MusicCacheDuration(types.IntPreference):
    show_in_api = True
    section = music
    name = "transcoding_cache_duration"
    default = 60 * 24 * 7
    verbose_name = "Transcoding cache duration"
    help_text = (
        "How many minutes do you want to keep a copy of transcoded tracks "
        "on the server? Transcoded files that were not listened in this interval "
        "will be erased and retranscoded on the next listening."
    )
    field_kwargs = {"required": False}


@global_preferences_registry.register
class MbidTaggedContent(types.BooleanPreference):
    show_in_api = True
    section = music
    name = "only_allow_musicbrainz_tagged_files"
    verbose_name = "Only allow Musicbrainz tagged files"
    help_text = (
        "Requires uploaded files to be tagged with a MusicBrainz ID. "
        "Enabling this setting has no impact on previously uploaded files. "
        "You can use the CLI to clear files that don't contain an MBID or "
        "or enable quality filtering to hide untagged content from API calls. "
    )
    default = False


@global_preferences_registry.register
class JoinPhrases(types.StringPreference):
    show_in_api = True
    section = music
    name = "join_phrases"
    verbose_name = "Join Phrases"
    help_text = (
        "Used by the artist parser to create multiples artists in case the metadata "
        "is a single string. BE WARNED, changing the order or the values can break the parser in unexpected ways. "
        "It's MANDATORY to escape dots and to put doted variation before because the first match is used "
        r"(example : `|feat\.|ft\.|feat|` and not `feat|feat\.|ft\.|feat`.). ORDER is really important "
        "(says an anarchist). To avoid artist duplication and wrongly parsed artist data "
        "it's recommended to tag files with Musicbrainz Picard. "
    )
    default = (
        r"featuring | feat\. | ft\. | feat | with | and | & | vs\. | \| | \||\| |\|| , | ,|, |,|"
        r" ; | ;|; |;| versus | vs | \( | \(|\( |\(| Remix\) |Remix\) | Remix\)| \) | \)|\) |\)| x |"
        "accompanied by | alongside | together with | collaboration with | featuring special guest |"
        "joined by | joined with | featuring guest | introducing | accompanied by | performed by | performed with |"
        "performed by and | and | featuring | with | presenting | accompanied by | and special guest |"
        "featuring special guests | featuring and | featuring & | and featuring "
    )
    widget = widgets.Textarea
    field_kwargs = {"required": False}


@global_preferences_registry.register
class DefaultJoinPhrases(types.StringPreference):
    show_in_api = True
    section = music
    name = "default_join_phrase"
    verbose_name = "Default Join Phrase"
    help_text = (
        "The default join phrase used by artist parser"
        "For example: `artists = [artist1, Artist2]` will be displayed has : artist1.name, artis2.name"
        "Changing this value will not update already parsed artists"
    )
    default = ", "
    widget = widgets.Textarea
    field_kwargs = {"required": False}
