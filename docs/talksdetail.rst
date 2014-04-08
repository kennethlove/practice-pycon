*******************
``TalksDetailView``
*******************

We have one last section to address in the development of this project, which is showing the detail of a ``Talk`` and being able to do stuff with it, like move it to a new list, rate the talk, and leave notes about it. If had more time, we'd probably want to add in some sharing abilities, too, so people could coordinate their talk attendance, but I'll leave that as an exercise for the reader.

View
----

While our view will definitely get more complicated as it goes, let's start with something very basic.

.. code-block:: python

        class TalkDetailView(views.LoginRequiredMixin, generic.DetailView):
                model = models.Talk

                def get_queryset(self):
                    return self.model.objects.filter(talk_list__user=self.request.user)

We, of course, need an URL and template for it.

URL
^^^

Since this URL is all about a talk, let's make a new section in our ``talks/urls.py``:

.. code-block:: python

    talks_patterns = patterns(
        '',
        url('^d/(?P<slug>[-\w]+)/$', views.TalkDetailView.as_view(),
            name='detail'),
    )

And add it to our ``urlpatterns`` with its own namespace. 

.. code-block:: python

    url(r'^talks/', include(talks_patterns, namespace='talks')),

While this is, admittedly, a bit much for just one view, most of the time you'd end up with many views related to this one model and want to have them all in a common location.

Template
^^^^^^^^

And now let's set up ``talks/templates/talks/talk_detail.html``:

.. code-block:: html

    {% extends "_layouts/base.html" %}

    {% block title %}{{ object.name }} | Talks | {{ block.super }}{% endblock title %}

    {% block headline %}
    <h1>{{ object.name }}</h1>
    <h2>
        <span class="text-primary">{{ object.host }}</span>
        <strong>at {{ object.when }}</strong>
        in <span class="text-info">Room {{ object.room }}</span>
    </h2>
    {% endblock headline %}

    {% block content %}

        <div class="row">
            <div class="col-sm-8">
            </div>
            <div class="col-sm-4">
                <p><a href="{{ object.talk_list.get_absolute_url }}">Back to list</a></p>
            </div>
        </div>

    {% endblock content %}

It might seem like we have some strange bits of HTML and spacing, but we're going to fill those up soon.

Ratings
-------

We said earlier we wanted to be able to rate the talks. I think there are two criteria that are most useful for rating a talk: the talk itself, including slides and materials; and how well the speaker performed and seemed to know their subject. So let's add two fields to our ``Talk`` model:

.. code-block:: python

   talk_rating = models.IntegerField(blank=True, default=0)
   speaker_rating = models.IntegerField(blank=True, default=0)

We want both of these to be ``blank``-able because we want to be able to save talks without ratings without any forms complaining at us. We also want them to have a ``default`` of 0 for our existing items and just as a sane default.

Let's add a ``property`` to our model, too, to calculate the average of these two ratings:

.. code-block:: python

   [...]
   @property
   def overall_rating(self):
        if self.talk_rating and self.speaker_rating:
            return (self.talk_rating + self.speaker_rating) / 2
        return 0

Form
^^^^

If give a model ratings, it's going to want a form.

.. code-block:: python
   :linenos:
   :emphasize-lines: 8, 15-17

    [...]
    from crispy_forms.layout import Field, Fieldset
    [...]

    class TalkRatingForm(forms.ModelForm):
        class Meta:
            model = models.Talk
            fields = ('talk_rating', 'speaker_rating')

        def __init__(self, *args, **kwargs):
            super(TalkRatingForm, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.layout = Layout(
                Fieldset(
                    'Rating',
                    Field('talk_rating', css_class='rating'),
                    Field('speaker_rating', css_class='rating')
                ),
                ButtonHolder(
                    Submit('save', 'Save', css_class='btn-primary')
                )
            )

As you can see on line 4, we limit the fields to just the two rating fields. We also add them to a ``Fieldset`` with a caption of "Rating". We also gave both fields a ``css_class`` of ``'rating'``. We'll use this to apply some CSS and Javascript soon.

View
^^^^

Since we want to rate talks from the ``TalkDetailView``, we need to update that view to include the form we just created.

.. code-block:: python

    class TalkDetailView(views.LoginRequiredMixin, generic.DetailView):
        http_method_names = ['get', 'post']
        model = models.Talk

        def get_queryset(self):
            return self.model.objects.filter(talk_list__user=self.request.user)

        def get_context_data(self, **kwargs):
            context = super(TalkDetailView, self).get_context_data(**kwargs)
            obj = context['object']
            rating_form = forms.TalkRatingForm(self.request.POST or None,
                                               instance=obj)
            context.update({
                'rating_form': rating_form,
            })
            return context

        def post(self, request, *args, **kwargs):
            self.object = self.get_object()
            talk_form = forms.TalkRatingForm(request.POST or None,
                                             instance=self.object)
            if talk_form.is_valid():
                talk_form.save()

            return redirect(self.object)

Template
^^^^^^^^

And, finally, of course, we have to update ``talks/templates/talks/talk_detail.html`` to render the form.

.. code-block:: html

   [...]
   {% load crispy_forms_tags %}
   [...]

   <div class="col-sm-8">
       {% crispy rating_form %}
   </div>
   [...]

You should now be able to type in a rating and save that on the model. If both fields are there, the ``overall_rating`` property should give you their average.

jQuery Plugin
^^^^^^^^^^^^^

But I'm not really happy with typing in a number. I'd rather click a star and have that set the rating. So we'll visit `http://plugins.krajee.com <http://plugins.krajee.com>`_  and get their star rating plugin and put it to use.

When you download it, you'll get a directory of Javascript and a directory of CSS. Since this is, like our templates, app-specific, we'll create a ``static`` directory in our app to put these files into.

::

    mkdir -p talks/static/talks/{css,js}

Move the ``star-rating.min.css`` file into the ``css`` directory we just created and do the same with the ``star-rating.min.js`` file and the ``js`` directory. Back in our template, let's add in the necessary blocks and tags to load these items.

.. code-block:: html

   {% load static from staticfiles %}
   [...]

   {% block css %}
   <link href="{% static 'talks/css/star-rating.min.css' %}" rel="stylesheet">
   {% endblock css %}

   {% block js %}
   <script src="{% static 'talks/js/star-rating.min.js' %}"></script>
   {% endblock %}

Why use the ``{% static %}`` tag? This tag helps us if our files don't end up exactly in these directories after being pushed to a CDN or through some other process. It adds a slight bit of overhead compared to hardcoding the path to the file, but it's worth it for the convenience, I think.

Since we gave our fields the ``'rating'`` class, they should both show up with clickable stars for the ratings now.
