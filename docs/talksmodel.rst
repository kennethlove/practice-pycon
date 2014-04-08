***********
Talks model
***********

We need a model for our actual talks which will belong to a list. Eventually we'll want ratings and notes and such, but let's start with a simple model.

Model, take one
===============

.. code-block:: python
   :linenos:
   :emphasize-lines: 8-14, 19, 24

   from django.core.urlresolvers import reverse
   from django.db import models
   from django.template.defaultfilters import slugify
   from django.utils.timezone import utc


   class Talk(models.Model):
       ROOM_CHOICES = (
           ('517D', '517D'),
           ('517C', '517C'),
           ('517AB', '517AB'),
           ('520', '520'),
           ('710A', '710A')
       )
       talk_list = models.ForeignKey(TalkList, related_name='talks')
       name = models.CharField(max_length=255)
       slug = models.SlugField(max_length=255, blank=True)
       when = models.DateTimeField()
       room = models.CharField(max_length=10, choices=ROOM_CHOICES)
       host = models.CharField(max_length=255)

       class Meta:
           ordering = ('when', 'room')
           unique_together = ('talk_list', 'name')

       def __unicode__(self):
           return self.name

       def save(self, *args, **kwargs):
           self.slug = slugify(self.name)
           super(Talk, self).save(*args, **kwargs)


Like with our ``TalkList`` model, we want to ``slugify`` the name whenever we save an instance. We also provide a tuple of two-tuples of choices for our ``room`` field, which makes sure that whatever talks get entered all have a valid room and saves users the trouble of having to type the room number in every time.

Also, we want default ordering of the model to be by when the talk happens, in ascending order, and then by room number.

Form
====

We should create a form for creating talks. In ``forms.py``, let's add ``TalkForm``:

.. code-block:: python
   :linenos:
   :emphasize-lines: 26-32

   import datetime

   from django.core.exceptions import ValidationError
   from django.utils.timezone import utc
   [...]

   class TalkForm(forms.ModelForm):
       class Meta:
           fields = ('name', 'host', 'when', 'room')
           model = models.Talk

       def __init__(self, *args, **kwargs):
           super(TalkForm, self).__init__(*args, **kwargs)
           self.helper = FormHelper()
           self.helper.layout = Layout(
               'name',
               'host',
               'when',
               'room',
               ButtonHolder(
                   Submit('add', 'Add', css_class='btn-primary')
               )
           )

       def clean_when(self):
           when = self.cleaned_data.get('when')
           pycon_start = datetime.datetime(2014, 4, 11).replace(tzinfo=utc)
           pycon_end = datetime.datetime(2014, 4, 13, 17).replace(tzinfo=utc)
           if not pycon_start < when < pycon_end:
               raise ValidationError("'when' is outside of PyCon.")
           return when

This ``ModelForm`` should look pretty similar to the other ones we've created so far, but it adds a new method, ``clean_when``, which is called during the validation process and only on the ``when`` field.

We get the current value of ``when``, then check it against two ``datetime`` objects that represent the start and end dates of PyCon. So long as our submitted date is between those two ``datetime``\ s, we're happy.

Update ``TalkListDetailView``
=============================

So now we need to be able to add a ``Talk`` to a ``TalkList``. If you noticed on the ``TalkForm``, we don't pass through the ``talk_list`` field because we'll do this in the view. But we aren't going to create a custom view for this, even though we could. We'll just extend the ``TalkListDetailView`` to handle this new bit of functionality.

So, back in ``views.py``, let's update ``TalkListDetailView``:

.. code-block:: python
   :linenos:
   :emphasize-lines: 2, 10-11, 15-18, 20-29

   [...]
   from django.shortcuts import redirect
   [...]

   class TalkListDetailView(
       RestrictToOwnerMixin,
       views.PrefetchRelatedMixin,
       generic.DetailView
   ):
       form_class = forms.TalkForm
       http_method_names = ['get', 'post']
       model = models.TalkList
       prefetch_related = ('talks',)

       def get_context_data(self, **kwargs):
           context = super(TalkListDetailView, self).get_context_data(**kwargs)
           context.update({'form': self.form_class(self.request.POST or None)})
           return context

       def post(self, request, *args, **kwargs):
           form = self.form_class(request.POST)
           if form.is_valid():
               obj = self.get_object()
               talk = form.save(commit=False)
               talk.talk_list = obj
               talk.save()
           else:
               return self.get(request, *args, **kwargs)
           return redirect(obj)

So, what are we doing here? We set a ``form_class`` attribute on the view, and, if this was a ``FormView`` derivative, it would know what to do with that, but it's not so we're really just providing this for our own convenience.

Then, in ``get_context_data``, we set up the normal context dictionary before adding a ``self.request.POST or None``\ -seeded instance of the form to the dict.

And, finally, in ``post``, which is now allowed by the ``http_method_names`` attribute, we build a new instance of the form, check to see if it's valid, and save it if it is, first adding the ``TalkList`` to the ``Talk``.

Template
--------

Now we need to update the template for the ``TalkListDetailView``, so open up ``talks/templates/talks/talklist_detail.html`` and add the following:

.. code-block:: html

   {% load crispy_forms_tags %}
   [...]

   <div class="panel panel-default">
       <div class="panel-heading">
           <h1 class="panel-title">Add a new talk</h1>
       </div>
       <div class="panel-body">
           {% crispy form %}

       </div>
   </div>

The ``.panel`` div goes in the sidebar near the "Back to lists" and "Edit this list" links.

We're not doing anything interesting in this new snippet, just having ``django-crispy-forms`` render the form for us.

``TalkListListView``
====================

Now that we can add talks to lists, we should probably show a count of the talks that a list has.

Pop open ``talks/templates/talks/talklist_list.html`` and, where we have a link to each ``TalkList``, add:

.. code-block:: html

        <span class="badge">{{ object.talks.count }}</span>

Now, while this works, this adds an extra query for every ``TalkList`` our user has. If someone has a ton of lists, this could get very expensive.

.. note::
   This is normally where I'd add in ``django-debug-toolbar`` and suggest you do the same. Install it with ``pip`` and follow the instructions online.

In ``views.py``, let's fix this extra query.

.. code-block:: python
   :linenos:
   :emphasize-lines: 2, 13

   [...]
   from django.db.models import Count
   [...]

   class TalkListListView(
       RestrictToOwnerMixin,
       generic.ListView
   ):
   model = models.TalkList

   def get_queryset(self):
       queryset = super(TalkListListView, self).get_queryset()
       queryset = queryset.annotate(talk_count=Count('talks'))
       return queryset

We're using Django's ``Count`` annotation to add a ``talk_count`` attribute to each instance in the queryset, which means all of the counting is done by our database and we don't ever have to touch the ``Talk`` related items.

Go back to the template and change ``{{ object.talks.count }}`` to ``{{ object.talk_count }}``.

Show the talks on a list
========================

We aren't currently showing the talks that belong to a list, so let's fix that.

In ``talks/templates/talklist_detail.html``, the leftside column should contain:

.. code-block:: html

    <div class="col-sm-6">
        {% for talk in object.talks.all %}
            {% include 'talks/_talk.html' %}
        {% endfor %}
    </div>

This includes a new template, ``talks/templates/talks/_talk.html`` for every talk on a list. Here's that new template:

.. code-block:: html
   :linenos:

   <div class="panel panel-info">
       <div class="panel-heading">
           <a class="close" aria-hidden="true" class="pull-right" href="#">&times;</a>
           <h1 class="panel-title"><a href="{{ talk.get_absolute_url }}">{{ talk.name }}</a></h1>
       </div>
       <div class="panel-body">
           <p class="bg-primary" style="padding: 15px"><strong>{{ talk.when }}</strong> in <strong>{{ talk.room }}</strong></p>
           <p>by <strong>{{ talk.host }}</strong>.</p>
       </div>
   </div>


``TalkListRemoveTalkView``
==========================

Since we can add talks to a list, we should be able to remove them. Let's make a new view in ``views.py``

.. code-block:: python
   :linenos:

   class TalkListRemoveTalkView(generic.RedirectView):
       model = models.Talk

       def get_redirect_url(self, *args, **kwargs):
           return self.talklist.get_absolute_url()

       def get_object(self, pk, talklist_pk):
           try:
               talk = self.model.objects.get(
                   pk=pk,
                   talk_list_id=talklist_pk,
                   talk_list__user=self.request.user
               )
           except models.Talk.DoesNotExist:
               raise Http404
           else:
               return talk

       def get(self, request, *args, **kwargs):
           self.object = self.get_object(kwargs.get('pk'),
                                         kwargs.get('talklist_pk'))
           self.talklist = self.object.talk_list
           messages.success(
               request,
               u'{0.name} was removed from {1.name}'.format(
                   self.object, self.talklist))
           self.object.delete()
           return super(TalkListRemoveTalkView, self).get(request, *args,
                                                          **kwargs)

Since we're using a ``RedirectView``, we need to supply a ``redirect_url`` for the view to send requests to once the view is finished, and since we need it to be based off of a related object that we won't know until the view is resolved, we supply this through the ``get_redirect_url`` method.

Normally ``RedirectView``\ s don't care about models or querysets, but we provide ``get_object`` on our view which expects the ``pk`` and ``talklist_pk`` that will come in through our URL (when we build it in a moment). We, again, check to make sure the current user owns the list and that the talk belongs to the list.

And, we've overridden ``get`` completely to make this all work. ``get`` gets our object with the URL ``kwargs``, grabs the ``TalkList`` instance for later use, gives the user a message, and then actually deletes the ``Talk``.

URL
---

Like all views, our new one needs a URL.

.. code-block:: python

    url(r'^remove/(?P<talklist_pk>\d+)/(?P<pk>\d+)/$',
        views.TalkListRemoveTalkView.as_view(),
        name='remove_talk'),

We add this to ``list_patterns``, still, and then update ``talks/templates/talks/_talk.html``, replacing the ``'#'`` in the ``.close`` link with ``{% url 'talks:lists:remove_talk` talk.talk_list_id talk.id %}``. We can now remove talks from a list.

``TalkListScheduleView``
========================

The views we've been creating are handy but aren't necessarily the cleanest for looking at, printing off, or keeping up on a phone, so let's make a new view that expressly aimed at those purposes.

In ``views.py``, we're going to add:

.. code-block:: python

    class TalkListScheduleView(
        RestrictToOwnerMixin,
        views.PrefetchRelatedMixin,
        generic.DetailView
    ):
        model = models.TalkList
        prefetch_related = ('talks',)
        template_name = 'talks/schedule.html'

This view is very similar to our ``TalkListDetailView`` but has a specific template, no added form, and no ``post`` method. To round it out, let's set up the URL and the template.

URL
---

.. code-block:: python

    url(r'^s/(?P<slug>[-\w]+)/$', views.TalkListScheduleView.as_view(),
        name='schedule'),

Almost identical to the URL for our ``TalkListDetailView``, it just changes the ``d`` to an ``s``.

.. note::
   This could be done entirely through arguments to the view from the url or querystring, but that would required more conditional logic in our view and/or our template, which I think is, in this case, a completely unnecessary complication.

Template
--------

Our new template file is, of course, ``talks/templates/talks/schedule.html``

.. code-block:: html
   :linenos:
   :emphasize-lines: 11, 12, 15, 27

    {% extends '_layouts/base.html' %}

    {% block title %}{{ object.name }} | Lists | {{ block.super }}{% endblock title %}

    {% block headline %}
    <h1>{{ object.name }}</h1>
    <h2>Your Lists</h2>
    {% endblock headline %}

    {% block content %}
    {% regroup object.talks.all by when|date:"Y/m/d" as day_list %}
    {% for day in day_list %}
    <div class="panel panel-default">
        <div class="panel-heading">
            <h1 class="panel-title">{{ day.grouper }}</h1>
        </div>
        <table class="table">
            <thead>
                <tr>
                    <th>Room</th>
                    <th>Time</th>
                    <th>Talk</th>
                    <th>Presenter(s)</th>
                </tr>
            </thead>
            <tbody>
                {% for talk in day.list %}
                <tr>
                    <td>{{ talk.room }}</td>
                    <td>{{ talk.when|date:"h:i A" }}</td>
                    <td>{{ talk.name }}</td>
                    <td>{{ talk.host }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endfor %}
    {% endblock %}

The special thing about this template is how we regroup the talks. We want them grouped and sorted by their dates. Using ``{% regroup %}`` gives us this ability and a new object that is a list of dictionaries with two keys, ``grouper`` which holds our day; and ``list``, which is a list of the instances in that group.
