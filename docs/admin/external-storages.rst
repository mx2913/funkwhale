Using external storages to store Funkwhale content
==================================================

By default, Funkwhale will store user-uploaded and related media such as audio files,
transcoded files, avatars and album covers on a server directory.

However, for bigger instances or more complex deployment scenarios, you may want
to use distributed or external storages.

S3 and S3-compatible servers
----------------------------

.. note::

    This feature was released in Funkwhale 0.19 and is still considered experimental.
    Please let us know if you see anything unusual while using it.

Funkwhale supports storing media files Amazon S3 and compatible implementations such as Minio or Wasabi.

In this scenario, the content itself is stored in the S3 bucket. Non-sensitive media such as
album covers or user avatars are served directly from the bucket. However, audio files
are still served by the reverse proxy, to enforce proper authentication.

To enable S3 on Funkwhale, add the following environment variables::

    AWS_ACCESS_KEY_ID=
    AWS_SECRET_ACCESS_KEY=
    AWS_STORAGE_BUCKET_NAME=
    # An optional bucket subdirectory were you want to store the files. This is especially useful
    # if you plan to use share the bucket with other services
    # AWS_LOCATION=

    # If you use a S3-compatible storage such as minio, set the following variable
    # the full URL to the storage server. Example:
    #   AWS_S3_ENDPOINT_URL=https://minio.mydomain.com
    # AWS_S3_ENDPOINT_URL=

Then, edit your nginx configuration. On docker setups, the file is located at ``/srv/funkwhale/nginx/funkwhale.template``,
and at ``/etc/nginx/sites-available/funkwhale.template`` on non-docker setups.

Replace the ``location /_protected/media`` block with the following::

    location ~ /_protected/media/(.+) {
        internal;
        # Needed to ensure DSub auth isn't forwarded to S3/Minio, see #932
        proxy_set_header Authorization "";
        proxy_pass $1;
    }

Add your S3 store URL to the ``img-src`` and ``media-src`` headers

.. code-block:: shell

    add_header Content-Security-Policy "...img-src 'self' https://<your-s3-URL> data:;...media-src https://<your-s3-URL> 'self' data:";

Then restart Funkwhale and nginx.

From now on, media files will be stored on the S3 bucket you configured. If you already
had media files before configuring the S3 bucket, you also have to move those on the bucket
by hand (which is outside the scope of this guide).

.. note::

    At the moment, we do not support S3 when using Apache as a reverse proxy.

.. note::

    If you are attempting to integrate your docker deployment with an existing nginx webserver, 
    such as the one provided by `linuxserver/swag <https://docs.linuxserver.io/images/docker-swag>`_ 
    (formerly `linuxserver/letsencrypt <https://docs.linuxserver.io/images/docker-swag#migrating-from-the-old-linuxserver-letsencrypt-image>`_),
    you may run into an issue where an additional ``Content-Security-Policy`` header appears in responses from the server, 
    without the newly included S3 URL values.

    In this case, you can suppress the extraneous ``Content-Security-Policy`` header by specifying it in a ``proxy_hide_header`` 
    `directive <http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_hide_header>`_ in the ``location /`` block.

    .. code-block:: shell

        location / {
            proxy_pass http://funkwhale:80;
            # ... 
            # ... include the rest of the preset directives
            # ...
            proxy_hide_header Content-Security-Policy;
        }


Serving audio files directly from the bucket
********************************************

Depending on your setup, you may want to serve audio files directly from the S3 bucket
instead of proxying them through Funkwhale, e.g to reduce the bandwidth consumption on your server,
or get better performance.

You can achieve that by adding ``PROXY_MEDIA=false`` to your ``.env`` file.

When receiving a request on the stream endpoint, Funkwhale will check for authentication and permissions,
then issue a 302 redirect to the file URL in the bucket.

This URL is actually be visible by the client, but contains a signature valid only for one hour, to ensure
no one can reuse this URL or share it publicly to distribute unauthorized content.

.. note::

   If you are using Amazon S3, you will need to set your ``AWS_S3_REGION_NAME`` in the ``.env`` file to
   use this feature.

.. note::

    Since some Subsonic clients don't support 302 redirections, Funkwhale will ignore
    the ``PROXY_MEDIA`` setting and always proxy file when accessed through the Subsonic API.


Securing your S3 bucket
***********************

It's important to ensure your the root of your bucket doesn't list its content,
which is the default on many S3 servers. Otherwise, anyone could find out the true
URLs of your audio files and bypass authentication.

To avoid that, you can set the following policy on your bucket::

    {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                "*"
                ]
            },
            "Resource": [
                "arn:aws:s3:::<yourbucketname>/*"
            ],
            "Sid": "Public"
            }
        ]
    }

If you are using ``awscli``, you can store this policy in a ``/tmp/policy`` file, and
apply it using the following command::

    aws s3api put-bucket-policy --bucket <yourbucketname> --policy file:///tmp/policy

Troubleshooting
***************

No Resolver Found
^^^^^^^^^^^^^^^^^

Depending on your setup, you may experience the following issue when trying to stream
music directly from your S3-compatible store.

.. code-block:: shell

    [error] 2832#2832: *1 no resolver defined to resolve [address] client: [IP], server: [servername], request: "GET API request", host: "[your_domain]", referrer: "[your_domain/library]"

This happpens when the nginx config is unable to use your server's DNS resolver. This issue
is still under investigation, but in the meantime can be worked around by specifying a resolver
in your ``funkwhale.template`` under the ``location ~/_protected/media/(.+)`` section.

.. code-block:: shell

    location ~ /_protected/media/(.+) {
        resolver 1.1.1.1;
        internal;
        proxy_set_header Authorization "";
        proxy_pass $1;
    }

No Images or Media Loading
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are serving media from an S3-compatible store, you may experience an issue where
nothing loads in the front end. The error logs in your browser may show something like
the following:

.. code-block:: text

    Content Security Policy: The page's settings blocked the loading of a resource at https://<your-s3-url> ("img-src")
    Content Security Policy: The page's settings blocked the loading of a resource at https://<your-s3-url> ("media-src")

This happens when your S3 store isn't defined in the ``Content-Security-Policy`` headers
in your Nginx files. To resolve the issue, add the base URL of your S3 store to the ``img-src``
and ``media-src`` headers and reload nginx.

.. code-block:: shell

    add_header Content-Security-Policy "...img-src 'self' https://<your-s3-URL> data:;...media-src https://<your-s3-URL> 'self' data:";

Broken Images in Audio Player On Page Reload
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are serving media directly from an S3-compatible store, you may find that images 
in the queue and the player won't load after the page is refreshed. This happens if the 
generated URL has expired and the authorization is no longer valid. You can extend the expiry time
using the following setting in your ``.env`` file:

.. code-block:: shell

    # The default value is 3600 (60 mins). The maximum is 604800 (7 days)
    AWS_QUERYSTRING_EXPIRE=604800
