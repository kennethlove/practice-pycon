Django
======

Now that we have an active ``virtualenv``, we need to install Django. ``pip install django==1.6.2`` will install the version of Django that we want for this project and give us the ``django-admin.py`` command. To start our project, we then run ``django-admin.py startproject survivalguide``. Then ``cd`` into the ``survivalguide`` directory.

Git
---

This directory (``pycon/survivalguide/``) is where we want the base of our project to be as far as git and Heroku are concerned, so we'll go ahead and do a ``git init``. We also should add the following ``.gitignore`` file:

::

    *.pyc
    db.sqlite3


Database
--------

For the purposes of this demo, we aren't going to use a *real* database like Postgres locally so we don't have to install ``psycopg2``. We'll stick with SQLite3, but feel free to swap it out for a local Postgres database if you want.

We do need to run ``python manage.py syncdb`` to get our default tables set up. Go ahead and create a superuser, too.

Template Dirs
-------------

We'll need some site-wide templates before long so we'll create a directory to hold them all with ``mkdir templates``. We need to add that to ``survivalguide/settings.py`` as such:

.. code-block:: python

    TEMPLATE_DIRS = (
        os.path.join(BASE_DIR, 'templates'),
    )

We have to be sure and include the trailing comma since ``TEMPLATE_DIRS`` must be a tuple.

Global Layouts
--------------

My convention for site-wide templates (and partials, both site-wide and app-specific) is to prepend the file or directory name with an ``_``, so inside ``templates`` make a new directory named ``_layouts``.

Inside there, we need to touch ``base.html`` and give it the following code:

.. code-block:: html

    <!DOCTYPE>
    <html>
    <head>
        <title>{% block title %}PyCon Survival Guide{% endblock title %}</title>
        <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">
        <style>
            body {
                padding-bottom: 20px;
                padding-top: 70px;
            }
            .messages {
                list-style: none;
            }
        </style>
        {% block css %}{% endblock css %}
    </head>
    <body>
        <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
          <div class="container">
            <div class="navbar-header">
              <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
              </button>
              <a class="navbar-brand" href="#">PyCon Survival Guide</a>
            </div>
            <div class="navbar-collapse collapse">
            </div><!--/.navbar-collapse -->
          </div>
        </div>
        <div class="jumbotron">
            <div class="container">{% block headline %}{% endblock headline %}</div>
        </div>
        <div class="container">
            {% block content %}{% endblock content %}
        </div>
        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
        {% block js %}{% endblock js %}
    </body>
    </html>
