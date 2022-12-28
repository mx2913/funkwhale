# Install Funkwhale using Docker

Funkwhale is available as a containerized application. This enables you to run each service in containers rather than install them on your server. You can run Funkwhale using [Docker](https://docker.com) and Docker-Compose.

```{note}
This guide assumes you are using a [Debian](https://debian.org)-based system.
```

```{contents}
:local:
```

## Before you begin

- Set a `FUNKWHALE_VERSION` variable to the version you want to install. You will use this version for all commands in this guide.

  ```{parsed-literal}
  export FUNKWHALE_VERSION={sub-ref}`version`
  ```

- Install [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/).
- Install `curl`.

  ```{code-block} sh
  sudo apt update # update apt cache
  sudo apt install curl
  ```

## 1. Download the project files

1. Create the project directory structure.

   ```{code-block} sh
   mkdir /srv/funkwhale /srv/funkwhale/nginx
   ```

2. Navigate to the project directory

   ```{code-block} sh
   cd /srv/funkwhale
   ```

3. Download the `docker-compose` template. This contains information about the containers and how they work together.

   ```{code-block} sh
   curl -L -o /srv/funkwhale/docker-compose.yml "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/${FUNKWHALE_VERSION}/deploy/docker-compose.yml"
   ```

That's it! You've set up your project files.

## 2. Set up your environment file

The environment file contains options you can use to control your Funkwhale pod. Follow these steps to get a working environment up and running.

1. Download the `.env` template to your `/srv/funkwhale` directory.

   ```{code-block} sh
   curl -L -o /srv/funkwhale/.env "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/${FUNKWHALE_VERSION}/deploy/env.prod.sample"
   ```

2. Update `FUNKWHALE_VERSION` in the `.env` file to the `$FUNKWHALE_VERSION` variable you set earlier.

   ```{code-block} sh
   sed -i "s/FUNKWHALE_VERSION=latest/FUNKWHALE_VERSION=$FUNKWHALE_VERSION/" .env
   ```

3. Reduce the permissions on your `.env` file to `600`. This means that only your user can read and write this file.

   ```{code-block} sh
   chmod 600 /srv/funkwhale/.env
   ```

4. Generate a secret key for Django. This keeps your Funkwhale data secure. Do not share this key with anybody.

   ```{code-block} sh
   openssl rand -base64 45
   ```

5. Open the `.env` file in a text editor. For this example, we will use `nano`.

   ```{code-block} sh
   nano /srv/funkwhale/.env
   ```

6. Update the following settings:

   - Paste the secret key in the `DJANGO_SECRET_KEY` field.
   - Populate the `FUNKWHALE_HOSTNAME` field with the URL of your server.

7. Hit {kbd}`ctrl + x` then {kbd}`y` to save the file and close `nano`.

You're done! Your environment file is now ready to go. You can check out a full list of configuration options in our Environment file guide.

## 3. Set up Funkwhale

Once you've filled in your environment file, you can set up Funkwhale. Follow these steps to create your database and create a superuser.

1. Pull the containers to download all the required services.

   ```{code-block} sh
   cd /srv/funkwhale
   docker-compose pull
   ```

2. Bring up the database container so you can run the database migrations.

   ```{code-block} sh
   docker-compose up -d postgres
   ```

3. Run the database migrations.

   ```{code-block} sh
   docker-compose run --rm api python manage.py migrate
   ```

   ````{note}
   You may see the following warning when applying migrations:

      ```{code-block} text
      "Your models have changes that are not yet reflected in a migration, and so won't be applied."
      ```

   You can safely ignore this warning.
   ````

4. Create your superuser.

   ```{code-block} sh
   docker-compose run --rm api python manage.py createsuperuser
   ```

5. Launch all the containers to bring up your pod.

   ```{code-block} sh
   docker-compose up -d
   ```

That's it! Your Funkwhale pod is now up and running.

## 4. Set up your reverse proxy

Funkwhale requires a reverse proxy to serve content to users. We recommend using [Nginx](https://nginx.com) to handle requests to your container. To do this:

1. Install Nginx.

   ```{code-block} sh
   sudo apt-get update
   sudo apt-get install nginx
   ```

2. Download the Nginx templates from Funkwhale.

   ```{code-block} sh
   sudo curl -L -o /etc/nginx/funkwhale_proxy.conf "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/$FUNKWHALE_VERSION/deploy/funkwhale_proxy.conf"
   sudo curl -L -o /etc/nginx/sites-available/funkwhale.template "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/$FUNKWHALE_VERSION/deploy/docker.proxy.template"
   ```

3. Create an Nginx template with details from your `.env` file.

   ```{code-block} sh
   # Log in to a root shell.

   sudo su

   # Create an Nginx configuration using the Funkwhale template with details from your `.env` file.

   set -a && source /srv/funkwhale/.env && set +a
   envsubst "`env | awk -F = '{printf \" $%s\", $$1}'`" \
      < /etc/nginx/sites-available/funkwhale.template \
      > /etc/nginx/sites-available/funkwhale.conf

   # Enable the configuration so that Nginx serves it.

   ln -s /etc/nginx/sites-available/funkwhale.conf /etc/nginx/sites-enabled/

   # Exit the root shell.

   exit
   ```

That's it! You've created your Nginx file. Run the following command to check the `.env` details populated correctly.

```{code-block} sh
grep '${' /etc/nginx/sites-enabled/funkwhale.conf
```

### Override default Nginx templates

The frontend container ships default Nginx templates which serve content to the reverse proxy. These files read variables from your `.env` file to correctly serve content. In some cases, you might want to override these defaults. To do this:

1. Create a `/srv/funkwhale/nginx` directory to house your files.

   ```{code-block} sh
   mkdir /srv/funkwhale/nginx
   ```

2. Download the Nginx template files to the `/srv/funkwhale/nginx` directory.

   ```{code-block} sh
   curl -L -o /srv/funkwhale/nginx/funkwhale.template "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/${FUNKWHALE_VERSION}/deploy/docker.nginx.template"
   curl -L -o /srv/funkwhale/nginx/funkwhale_proxy.conf "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/${FUNKWHALE_VERSION}/deploy/docker.funkwhale_proxy.conf"
   ```

3. Make any changes you want to make to these files.
4. Open your `docker-compose.yml` file in a text editor. For this example, we will use `nano`.

   ```{code-block} sh
   nano /srv/funkwhale/docker-compose.yml
   ```

5. Uncomment the lines in the `volumes` section of the `front` service by deleting the `#` in front of them.

   ```{code-block} yaml
   version: "3"
   services:
      front:
         volumes:
            # Uncomment if you want to use your previous nginx config, please let us
            # know what special configuration you need, so we can support it with out
            # upstream nginx configuration!
            - "./nginx/funkwhale.template:/etc/nginx/conf.d/funkwhale.template:ro"
            - "./nginx/funkwhale_proxy.conf:/etc/nginx/funkwhale_proxy.conf:ro"
   ```

6. Bring the `front` container up again to pick up the changes.

   ```{code-block} sh
   docker-compose up -d front
   ```

That's it! The container mounts your custom nginx files and uses its values to serve Funkwhale content. To revert to the default values, comment out the volumes by adding a `#` in front of them and bring the `front` container back up.

## 5. Set up TLS

To enable your users to connect to your pod securely, you need to set up {abbr}`TLS (Transport Layer Security)`. To do this, we recommend using the <acme.sh> script.

1. Log in as the superuser account to run these commands.

   ```{code-block} sh
   su
   ```

2. Create the `/etc/certs` folder to store the certificates.

   ```{code-block} sh
   mkdir /etc/certs
   ```

3. Download and run `acme.sh`. Replace `my@example.com` with your email address.

   ```{code-block} sh
   curl https://get.acme.sh | sh -s email=my@example.com
   ```

4. Generate a certificate. Replace `example.com` with your Funkwhale pod name. Use `/srv/funkwhale/front` as your web root folder.

   ```{code-block} sh
   acme.sh --issue -d example.com -w /srv/funkwhale/front
   ```

5. Install the certificate to your Nginx config. Replace `example.com` with your Funkwhale pod name.

   ```{code-block} sh
   acme.sh --install-cert -d example.com \
   --key-file       /etc/certs/key.pem  \
   --fullchain-file /etc/certs/cert.pem \
   --reloadcmd     "service nginx force-reload"
   ```

That's it! acme.sh renews your certificate every 60 days, so you don't need to worry about renewing it.
