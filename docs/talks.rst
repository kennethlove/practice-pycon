*****************
The ``talks`` app
*****************

Now we can get to the meat of our project, the talks app.

``startapp``
------------

To start our app, we can to tell Django to give us some boilerplate right away with ``python manage.py startapp talks``. We want app names to be plural, generally, as they usually concern themselves with multiple model instances and work around them.

This will give us a structure similar to:

::

    /talks
    ├── __init__.py
    ├── admin.py
    ├── models.py
    ├── tests.py
    ├── views.py


We'll start off with the ``models.py`` in here.

.. note::

   I'll be giving paths relative to the ``talks/`` directory from here on out, so be sure to adjust them in your head as needed. Most text editors seem to offer a fuzzy file finder now, so editing should be fairly painless.

``TalkList`` model
------------------

We want to be able to organize our talks into lists, things like "Attend or Else" and "Watch Online". So the first thing we should probably have is a model for the list. Open up ``models.py`` and add the following:

.. code-block:: python
   :linenos:
   :emphasize-lines: 4,10,13,19,23

    from django.contrib.auth.models import User
    from django.core.urlresolvers import reverse
    from django.db import models
    from django.template.defaultfilters import slugify


    class TalkList(models.Model):
        user = models.ForeignKey(User, related_name='lists')
        name = models.CharField(max_length=255)
        slug = models.SlugField(max_length=255, blank=True)

        class Meta:
            unique_together = ('user', 'name')

        def __unicode__(self):
            return self.name

        def save(self, *args, **kwargs):
            self.slug = slugify(self.name)
            super(TalkList, self).save(*args, **kwargs)

        def get_absolute_url(self):
            return reverse('talks:lists:detail', kwargs={'slug': self.slug})


Our model ties ``TalkList`` instances to a user, makes sure each list has a unique name per user, runs ``slugify`` on the name so we can use it in our URL, and provides an URL to get an individual list. But, what about that URL? What's with the colons in it?

URLs
----

To make our URLs work like that, we need to set up three things and bring in a couple of namespaces.

First, let's make a placeholder in our ``views.py`` file.

.. code-block:: python

   from django.http import HttpResponse
   from django.views import generic


   class TalkListDetailView(generic.View):
       def get(self, request, *args, **kwargs):
           return HttpResponse('A talk list')

Now, we need to create ``urls.py`` inside ``talks/`` and add the followng:

.. code-block:: python
   :linenos:
   :emphasize-lines: 15

    from __future__ import absolute_import

    from django.conf.urls import patterns, url, include

    from . import views


    lists_patterns = patterns(
        '',
        url(r'^$', views.TalkListDetailView.as_view(), name='detail'),
    )

    urlpatterns = patterns(
        '',
        url(r'^lists/', include(lists_patterns, namespace='lists')),
    )

This line sets up an internal namespace of ``lists`` for all of our ``TalkList``-specific URLs. Now we need to add the ``talks`` namespace that our ``get_absolute_url`` mentioned.

Open up ``survivalguide/urls.py`` and add:

.. code-block:: python

    url(r'^talks/', include('talks.urls', namespace='talks')),

This sets up the ``talks`` namespace.

``south``
---------

Now, before we actually create the model, we should add ``south`` into the mix. ``pip install south`` will install it and we need to add ``'south'`` to our ``INSTALLED_APPS``. Since ``south`` has a model of its own, we also need to run ``python manage.py syncdb`` again to add it.

We should now add our ``'talks'`` app to ``INSTALLED_APPS`` and, instead of running ``syncdb``, we should run ``python manage.py schemamigration --initial talks``. ``south`` will create a migration that generates our database table and put it in the ``migrations/`` directory. Then we apply it with ``python manage.py migrate``.

.. note::

   ``python manage.py schemamigration`` is a really long command to have to type repeatedly, so I recommend creating a shell alias for it to save yourself some time.

.. warning::

   Django 1.7 introduces an internal migration tool much like ``south``. This tutorial does not cover that tool. While ``south`` will likely work with Django 1.7, you should use the new tool instead.

Default list
------------

Now that we have a model and a database table, let's make our ``SignUpView`` automatically create a default list for everyone. Open ``survivalguide/views.py`` and change ``SignUpView`` to match this:

.. code-block:: python
   :linenos:
   :emphasize-lines: 13-16

   [...]
   from talks.models import TalkList
   [...]

    class SignUpView(views.AnonymousRequiredMixin, views.FormValidMessageMixin,
                     generic.CreateView):
        form_class = RegistrationForm
        form_valid_message = "Thanks for signing up! Go ahead and login."
        model = User
        success_url = reverse_lazy('login')
        template_name = 'accounts/signup.html'

        def form_valid(self, form):
            resp = super(SignUpView, self).form_valid(form)
            TalkList.objects.create(user=self.object, name='To Attend')
            return resp
