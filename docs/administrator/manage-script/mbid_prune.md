# Delete funkwhale objects that don't have a Musicbrainz id

If you enable the option to [only allow MusicBrainz content](../configuration/instance-settings.md) on your pod after you've uploaded content,you can to use this command to prune content that doesn't have a MusicBrainz ID to make your database more consistent.

```{warning}
This action **does not** send a notification to your users before content is removed. You may want to warm them before.
```

```{warning}
Running `prune_non_mbid_content` with the `--no-dry-run` flag is irreversible. Make sure you [back up your data](../upgrade/backup.md).
```

::::{tab-set}

:::{tab-item} Debian
:sync: debian

```{code-block} sh
venv/bin/funkwhale-manage prune_non_mbid_content
```

:::

:::{tab-item} Docker
:sync: docker

```{code-block} sh
sudo docker compose run --rm api funkwhale-manage prune_non_mbid_content
```

:::
::::

```{note}
The command excludes tracks that are in users' favorites, playlists, and listen history. To include these tracks, add the corresponding flags:

- `--include-favorites-content`
- `--include-listened-content`
- `--include-playlist-content`
```
