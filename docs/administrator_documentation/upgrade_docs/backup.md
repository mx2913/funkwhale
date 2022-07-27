# Back up your Funkwhale instance

Before performing big changes, we recommend you back up your database and media files. Follow the instructions in this guide to back up your instance.

1. Back up your database.

   ::::{tab-set}

   :::{tab-item} Debian
   :sync: debian

   ```{code} bash
   sudo -u postgres -H pg_dumpall -c funkwhale > /path/to/your/backup/dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
   ```

   :::

   :::{tab-item} Docker
   :sync: docker

   ```{code} bash
   docker-compose exec postgres pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
   ```

   :::
   ::::

2. Back up your media files. In this example we use [rsync](https://rsync.samba.org) to back up the files.

   ::::{tab-set}

   :::{tab-item} Debian
   :sync: debian

   ```{code} bash
   rsync -avzhP /srv/funkwhale/data/media /path/to/your/backup/media
   rsync -avzhP /srv/funkwhale/data/music /path/to/your/backup/music
   ```

   :::

   :::{tab-item} Docker
   :sync: docker

   ```{code} bash

   rsync -avzhP /srv/funkwhale/data/media /path/to/your/backup/media
   rsync -avzhP /srv/funkwhale/data/music /path/to/your/backup/music
   ```

   :::
   ::::

3. Back up your configuration files.

   ::::{tab-set}

   :::{tab-item} Debian
   :sync: debian

   ```{code} bash
   rsync -avzhP /srv/funkwhale/config/.env /path/to/your/backup/.env
   ```

   :::

   :::{tab-item} Docker
   :sync: docker

   ```{code} bash
   rsync -avzhP /srv/funkwhale/.env /path/to/your/backup/.env
   ```

   :::
   ::::

If you are performing regular backups, you may need deduplication and compression to keep the size down. In this case, a tool like [`borg`](https://www.borgbackup.org/) is more appropriate.

## Restore a backup

### Restore your files

To restart your files, do the following:

1. Rename your current file directories.

   ```{code} bash
   mv /srv/funkwhale/data/media /srv/funkwhale/data/media.bak
   mv /srv/funkwhale/data/music /srv/funkwhale/data/music.bak
   ```

2. Restore your backed-up files to the original directories.

   ```{code} bash
   mv /patht/to/your/backup/media /srv/funkwhale/data/media
   mv /path/to/your/backup/music /srv/funkwhale/data/music
   ```

### Restore the database

To restore your database, do the following:

::::{tab-set}

:::{tab-item} Debian
:sync: debian

1. Restore your database backup with `pg_restore`:

   ```{code} bash
   sudo -u postgres psql -f /path/to/your/backup/dump.sql funkwhale
   ```

2. Run the `manage.py migrate` command to set up the database.

   ```{code} bash
   cd /srv/funkwhale/api
   poetry run python manage.py migrate
   ```

:::

:::{tab-item} Docker
:sync: docker

1. Restore your database backup.

   ```{code} bash
   docker-compose run --rm postgres psql -U postgres postgres -f "/path/to/your/backup/dump.sql"
   ```

2. Run the `manage.py migrate` command to set up the database.

   ```{code} bash
   docker-compose run --rm api python manage.py migrate
   ```

:::
::::
