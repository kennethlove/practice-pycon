**************
TalkList Views
**************

Our ``TalkLists`` need a few different views, so let's look at creating those.

``TalkListListView``
====================

We should have a view to show all of our lists. In ``views.py``:

.. code-block:: python
   :linenos:
   :emphasize-lines: 9-10

   [...]
   from braces import views

   from . import models

   class TalkListListView(views.LoginRequiredMixin, generic.ListView):
       model = models.TalkList

       def get_queryset(self):
           return self.request.user.lists.all()

There's not really anything fancy about this view other than overriding ``get_queryset``. We want users to only be able to view lists that they own, so this does that for us. We didn't specify a template, so Django will look for the default one at ``talks/talklist_list.html``.

Template
--------

Since this is an app and the templates are only for this app, I think it's best to put them in the app. This makes it easier to focus on the files for a specific app and it also makes it easier to make an app reusable elsewhere.

::

    mkdir -p talks/templates/talks
    touch talks/templates/talks/talklist_list.html


We need to namespace the template inside of a directory named the same as our app. Open up the template file and add in:

.. code-block:: html

    {% extends '_layouts/base.html' %}

    {% block title %}Lists | {{ block.super }}{% endblock title %}

    {% block headline %}<h1>Your Lists</h1>{% endblock headline %}

    {% block content %}
    <div class="row">
        <div class="col-sm-6">
            <ul class="list-group">
                {% for object in object_list %}
                <li class="list-group-item">
                    <a href="{{ object.get_absolute_url }}">{{ object }}</a>
                </li>
                {% empty %}
                <li class="list-group-item">You have no lists</li>
                {% endfor %}
            </ul>
        </div>
        <div class="col-sm-6">
            <p><a href="#" class="btn">Create a new list</a></p>
        </div>
    </div>
    {% endblock %}

URL
---

Now in our ``urls.py`` file, we need to update our ``list_patterns`` set of patterns.

.. code-block:: python

   [...]
   url(r'^$', views.TalkListListView.as_view(), name='list'),
   url(r'^d/(?P<slug>[-\w]+)/$', views.TalkListDetailView.as_view(),
       name='detail'),
   [...]

You'll notice that we replaced our old default URL (``r'^$'``) with our ``TalkListListView`` and put the ``TalkListDetailView`` under a new regex that captures a slug. Our model's ``get_absolute_url`` should still work fine.

``TalkListDetailView``
======================

Let's build out our actual detail view now. Back in ``views.py``:

.. code-block:: python
   :linenos:
   :emphasize-lines: 3, 7

   class TalkListDetailView(
       views.LoginRequiredMixin,
       views.PrefetchRelatedMixin,
       generic.DetailView
   ):
       model = models.TalkList
       prefetch_related = ('talks',)

       def get_queryset(self):
           queryset = super(TalkListDetailView, self).get_queryset()
           queryset = queryset.filter(user=self.request.user)
           return queryset

This mixin from ``django-braces`` lets us do a ``prefetch_related`` on our queryset to, hopefully, save ourselves some time in the database. Again, we didn't specify a template so we'll make one where Django expects.

Template
--------

Create the file ``talks/templates/talks/talklist_detail.html`` and add in:

.. code-block:: html

    {% extends '_layouts/base.html' %}

    {% block title %}{{ object.name }} | Lists | {{ block.super }}{% endblock title %}

    {% block headline %}
    <h1>{{ object.name }}</h1>
    <h2>Your Lists</h2>
    {% endblock headline %}

    {% block content %}
    <div class="row">
        <div class="col-sm-6">
            <p>Talks go here</p>
        </div>

        <div class="col-sm-6">
            <p><a href="{% url 'talks:lists:list' %}">Back to lists</a></p>
        </div>
    </div>
    {% endblock %}

A pretty standard Django template. We already have the URL so this should be completely wired up now.

``RestrictToUserMixin``
=======================

We had to override ``get_queryset`` in both of our views, which is kind of annoying. It would be nice to not have to do that, especially two different ways both times. Let's write a custom mixin to do this work for us.

.. code-block:: python

   class RestrictToUserMixin(views.LoginRequiredMixin):
       def get_queryset(self):
           queryset = super(RestrictToOwnerMixin, self).get_queryset()
           queryset = queryset.filter(user=self.request.user)
           return queryset

This does the same work as our ``get_queryset`` in ``TalkListDetailView``. Let's use it. In both views, add ``RestrictToUserMixin`` and take out the ``views.LoginRequiredMixin`` from ``django-braces`` since our new mixin provides that functionality too. Also remove the overrides of ``get_queryset`` from both views.


``TalkListCreateView``
======================

We want to be able to create a new ``TalkList``, of course, so let's create a ``CreateView`` for that. In ``views.py``, still, add a new class:

.. code-block:: python
   :linenos:
   :emphasize-lines: 6, 9, 10, 13-17

    [...]
    import .forms

    class TalkListCreateView(
        views.LoginRequiredMixin,
        views.SetHeadlineMixin,
        generic.CreateView
    ):
        form_class = forms.TalkListForm
        headline = 'Create'
        model = models.TalkList

        def form_valid(self, form):
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            return super(TalkListCreateView, self).form_valid(form)

This view has a ``form_class`` that we haven't created yet, so we'll need to do that soon. Also, we override ``form_valid``, which is called when the submitted form passes validation, and in there we create an instance in memory, assign the current user to the model instance, and then save for real and call ``super()`` on the method.

This view also brings in the ``SetHeadlineMixin`` and provides the ``headline`` attribute. We do this because we'll be using the same template for both create and update views and we don't want them to both have the same title and headline. This way we can control that from the view instead of having to create new templates all the time.

Let's create the form now.

``TalkListForm``
----------------

We don't yet have a ``talks/forms.py`` so go ahead and create it with the following content:

.. code-block:: python
   :linenos:
   :emphasize-lines: 13

    from __future__ import absolute_import

    from django import forms

    from crispy_forms.helper import FormHelper
    from crispy_forms.layout import Layout, ButtonHolder, Submit

    from . import models


    class TalkListForm(forms.ModelForm):
        class Meta:
            fields = ('name',)
            model = models.TalkList

        def __init__(self, *args, **kwargs):
            super(TalkListForm, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.layout = Layout(
                'name',
                ButtonHolder(
                    Submit('create', 'Create', css_class='btn-primary')
                )
            )


Nothing really different here from our earlier forms except for line 13 which restricts the fields that the form cares about to just the ``name`` field.

URL
---

As with all of our other views, we need to make an URL for creating lists. In ``talks/urls.py``, add the following line:

.. code-block:: python

    url(r'^create/$', views.TalkListCreateView.as_view(), name='create'),

Template
--------

And, again, we didn't specify a specific template name so Django expects ``talks/talklist_form.html`` to exist. Django will use this form for both ``CreateView`` and ``UpdateView`` views that use the ``TalkList`` model unless we tell it otherwise.

.. code-block:: html

    {% extends '_layouts/base.html' %}
    {% load crispy_forms_tags %}

    {% block title %}{{ headline }} | Lists | {{ block.super }}{% endblock title %}

    {% block headline %}
    <h1>{{ headline }}</h1>
    <h2>Your Lists</h2>
    {% endblock headline %}

    {% block content %}
    {% crispy form %}
    {% endblock content %}

You can see here were we use the ``{{ headline }}`` context item provided by the ``SetHeadlineMixin``. Now users should be able to create new lists.

``TalkListUpdateView``
======================

Anything we can create, we should be able to update so let's create a ``TalkListUpdateView`` in ``views.py``.

.. code-block:: python

    class TalkListUpdateView(
        RestrictToOwnerMixin,
        views.LoginRequiredMixin,
        views.SetHeadlineMixin,
        generic.UpdateView
    ):
        form_class = forms.TalkListForm
        headline = 'Update'
        model = models.TalkList

There isn't anything in this view that we haven't covered already. All that's left for it is to create the URL pattern.

URL
---

You should be getting the hang of this by now, so let's just add this line to our ``urls.py``:

.. code-block:: python

    url(r'^update/(?P<slug>[-\w]+)/$', views.TalkListUpdateView.as_view(),
        name='update'),


Global template changes
=======================

It's great that we've created all of these views but now there's no easy way to get to your views. Let's fix that by adding the following into ``_layouts/base.html`` next to our other navigation items inside the ``{% else %}`` clause:

.. code-block:: html

        <a href="{% url 'talks:lists:list' %}" class="btn btn-primary navbar-btn">Talk lists</a>

App template changes
====================

Our ``talks/talklist_list.html`` template should have a link to the ``TalkListCreateView`` so let's add that into the sidebar:

.. code-block:: html

        <p><a href="{% url 'talks:lists:create' %}" class="btn">Create a new list</a></p>

DeleteView?
===========

So what about a ``DeleteView`` for ``TalkList``\ ? I didn't make one for this example but it shouldn't be too hard of an exercise for the reader. Be sure to restrict the queryset to the logged-in user.
