``virtualenv``
==============

We want at least ``virtualenv`` installed so we don't have to pollute our global site-packages with our project-specific packages. This also lets us use our ``requirements.txt`` file locally and on Heroku when we deploy later.

``pip install virtualenv`` will install ``virtualenv`` for us. You may have to ``sudo`` this command or tell ``pip`` to install to your user space with the ``--user`` argument.

``virtualenvwrapper``
---------------------

If you're on a compatible system, install ``virtualenvwrapper`` with ``pip install virtualenvwrapper`` and add:

.. code-block:: sh

    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/local/bin/virtualenvwrapper.sh

to whatever config file your shell uses (e.g. ``~/.bashrc`` or ``~/.zshrc``). You may then need to restart your terminal or source the config file to make this active.

Make the ``virtualenv``
-----------------------

Now we want to actually create the ``virtualenv``.

With ``virtualenv``:

::

    virtualenv pycon-venv
    source pycon-venv/bin/activate

With ``virtualenvwrapper``:

::

    mkvirtualenv pycon
    workon pycon

Either way, your prompt should now change to show ``(pycon-venv)`` or ``(pycon)``.
