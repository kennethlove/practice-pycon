**********
Deployment
**********

Now we want to put this thing like on Heroku. We have several steps required before we can do this, so let's get started.

Postgres
--------

Since Heroku uses Postgres, we need to provide an adapter library for it. ``pip install psycopg2``. We also need to set up our database adapter in the project, so we need to also ``pip install dj-database-url`` and then open up ``settings.py``. We need to change ``DATABASES`` to look like:

.. code-block:: python

    import dj_database_url
    [...]

    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:////{0}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))
        )
    }

This will let us keep using our local SQLite database but use Heroku's database there.

WSGI and static files
---------------------

We also want to be able to serve our static files on Heroku, so we need to install ``dj-static`` or ``whitenoise``. Since ``dj-static`` doesn't support Python 3 yet, and we'd like to make sure our code is as future-friendly as possible, let's use ``whitenoise``.

``pip install whitenoise``, then open ``survivalguide/wsgi.py`` and, **after** the ``os.environ`` call, add ``from whitenoise.django import DjangoWhiteNoise``.

Then change the ``application`` line to wrap ``DjangoWhiteNoise`` around the ``get_wsgi_application()`` call.

``requirements.txt``
--------------------

We know that we're going to be running on gunicorn on Heroku, so we should ``pip install gunicorn`` before we go any further.

Now, we need to make sure Heroku can install our requirements. Back in the directory that contains ``manage.py``, we need to create a file named ``requirements.txt`` that holds all of the packages we've installed and their version. The easiest way to do this is:

::

    pip freeze --local > requirements.txt

If you look at this file, it should contain entries like:

::

    Django==1.6.2
    mistune==0.2.0

``Procfile``
------------

The last thing we need to do before we send things to Heroku is to create the ``Procfile`` that tells Heroku what to run. Ours just needs one process which looks like:

``web: gunicorn survivalguide.wsgi``

This tells Heroku to run ``gunicorn`` with our ``wsgi.py`` file.

Settings
--------

In our ``settings.py`` file, we need to set ``DEBUG`` to ``False`` and change ``ALLOWED_HOSTS`` to ``['*']`` since we don't yet know our Heroku URL.

Deploy
------

Now that we have everything collected and added into Git, we're ready to send our project to Heroku.

``heroku create`` will make Heroku create a new installation for us and set the Git remote locally. Now we can do ``git push heroku master`` and send all of our files to Heroku.

Once the process finishes, if you don't see any errors, you'll need to sync the database with ``heroku run python manage.py syncdb`` and create a superuser. Then ``heroku open`` will open your site in your browser.

