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

Migration
^^^^^^^^^

Since we've changed the model, we need to create a migration for it.

::

    python manage.py schemamigration --auto talks
    python manage.py migrate talks

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

As you can see on line 8, we limit the fields to just the two rating fields. We also add them to a ``Fieldset`` with a caption of "Rating". We also gave both fields a ``css_class`` of ``'rating'``. We'll use this to apply some CSS and Javascript soon.

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

Notes
-----

We also said we wanted to be able to write notes for the talks. I like to take notes in Markdown, so we'll save a field of Markdown, convert it to HTML, and save both of those in the model.

First, we need to change our ``Talk`` model. We'll add two fields, one to hold the Markdown and one to hold the HTML.

.. code-block:: python

   notes = models.TextField(blank=True, default='')
   notes_html = models.TextField(blank=True, default='', editable=False)

These fields are ``blank``-able like our ratings fields for much the same reasons, same with giving them a ``default``. The ``notes_html`` field gets ``editable=False`` because we don't want this field to be directly edited in ``ModelForm``\ s or the admin.

Of course, now that we've added fields to the model, we need to do another migration.

::

    python manage.py schemamigration --auto talks
    python manage.py migrate talks

But since we know we'll be getting Markdown and we know we want to convert it, we should come up with a way to do that easily and automatically.

First, let's ``pip install mistune``. ``mistune`` is a super-fast Python Markdown library that we can use to convert it to HTML. It's also super-easy to use. We need to import it at the top of the file and then we'll override the ``save`` method of our ``Talk`` model.

.. code-block:: python
   :linenos:
   :emphasize-lines: 5

   class Talk(models.Model):
        [...]
        def save(self, *args, **kwargs):
            self.slug = slugify(self.name)
            self.notes_html = mistune.markdown(self.notes)
            super(Talk, self).save(*args, **kwargs)

Template
^^^^^^^^

Now let's update our ``talks/templates/talks/talk_detail.html`` template to show the notes and the ratings. Add the following block before the ``.row`` div, at the top of ``{% block content %}``.

.. code-block:: html
   :linenos:

    {% if object.notes_html %}
    <div class="row">
        <div class="col-sm-8">
            <h3>Notes</h3>
            {{ object.notes_html|safe }}
        </div>
        <div class="col-sm-4">
            <div class="well">
                <table class="table table-condensed">
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Rating</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <th>Talk</th>
                            <td>{{ object.talk_rating }}</td>
                        </tr>
                        <tr>
                            <th>Speaker</th>
                            <td>{{ object.speaker_rating }}</td>
                        </tr>
                        <tr>
                            <th>Overall</th>
                            <td>{{ object.overall_rating }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <hr>
    {% endif %}

This will show any notes we've saved and our ratings. Currently the display of the ratings depends on us having notes saved, but that's something to fix later. Especially since we're likely to save notes **during** a talk but not save ratings until **after**.

Stars template tag
------------------

We're only printing out the number of stars something was given, though. While that's good information, it's not the most useful or attractive of outputs. Let's make a template tag to render a total number of stars and color some of them based on the rating.

First, we need to make a place to write the template tag. Tags always live with an app and are usually named for the app, so let's start with that.

::

    mkdir -p talks/templatetags/
    touch talks/templatetags/{__init__,talks_tags}.py

This will create the ``templatetags`` directory for us and stick in two files, ``__init__.py``, as usual, and ``talks_tags.py``, which is where we'll write the tag. Open that file in your editor and add in:

.. code-block:: python
   :linenos:
   :emphasize-lines: 6

   from django import template

   register = template.Library()


   @register.inclusion_tag('talks/_stars.html')
   def show_stars(count):
       return {
           'star_count': range(count),
           'leftover_count': range(count, 5)
       }

This tag is an inclusion tag which means it will render a template whenever we call it. Since it renders a template, we need to create that template. So open up ``talks/templates/talks/_stars.html`` and add:

.. code-block:: html

    {% for star in star_count %}
    <i class="glyphicon glyphicon-star" style="color:#fc0; font-size:24px"></i>
    {% endfor %}
    {% if leftover_count %}
        {% for star in leftover_count %}
        <i class="glyphicon glyphicon-star-empty" style="font-size:24px"></i>
        {% endfor %}
    {% endif %}

Nothing really fancy happening here, just printing out some stars based on the ``range`` that we created in the tag. We have some "magic numbers" here, but for the purposes of a demo, they're OK. In an actual production project, you'd want to set these rating upper limits in ``settings.py``.

Now let's open up ``talks/templates/talks/talk_detail.html`` and replace the three places where we print out ``{{ object.talk_rating }}``, etc, with ``{% show_stars object.talk_rating %}``. We also need to add ``{% load talks_tags %}`` at the top of the template.

Move talks between lists
------------------------

We'd also like to be able to move talks from one list to another, since we might change our minds about what list a talk should be on. We don't need to modify our models at all, since the ``ForeignKey`` between ``Talk`` and ``TalkList`` already exists, but we do need a new form and to modify our view and template.

Form
^^^^

In ``forms.py``, we're going to create a form called ``TalkTalkListForm`` and it'll look like:

.. code-block:: python
   :linenos:
   :emphasize-lines: 8-9

    class TalkTalkListForm(forms.ModelForm):
        class Meta:
            model = models.Talk
            fields = ('talk_list',)

        def __init__(self, *args, **kwargs):
            super(TalkTalkListForm, self).__init__(*args, **kwargs)
            self.fields['talk_list'].queryset = (
                self.instance.talk_list.user.lists.all())

            self.helper = FormHelper()
            self.helper.layout = Layout(
                'talk_list',
                ButtonHolder(
                    Submit('move', 'Move', css_class='btn-primary')
                )
            )

The only thing special that we're doing in this form is restricting the queryset for our ``talk_list`` field to the lists related to the user that owns the list that our current talk belongs to. This means we can't move our talk to someone else's list.

View
^^^^

Now we need to update the ``TalkDetailView``. Our final version of this view could be better refined, likely by moving things to other views that just redirect back to this one, but in the interest of keeping this demo short, we'll do it a slightly messier way.

In the view's ``get_context_data``, we need to instantiate the form we just created and add it to the context dictionary.

.. code-block:: python

    [...]
    list_form = forms.TalkTalkListForm(self.request.POST or None,
                                       instance=obj)
    context.update({
        'rating_form': rating_form,
        'list_form': list_form
    })

We also need to update the ``post`` method and add in some logic for handling *which* form was submitted. This is the part that would benefit from being separated out to other views.

.. code-block:: python

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'save' in request.POST:
            talk_form = forms.TalkRatingForm(request.POST or None,
                                             instance=self.object)
            if talk_form.is_valid():
                talk_form.save()

        if 'move' in request.POST:
            list_form = forms.TalkTalkListForm(request.POST or None,
                                               instance=self.object,
                                               user=request.user)
            if list_form.is_valid():
                list_form.save()

        return redirect(self.object)

Template
^^^^^^^^

Finally, we need to actually render the new form into the template. Open up ``talks/templates/talks/talk_detail.html`` and add ``{% crispy list_form %}`` in the ``.col-sm-4`` div near the "Back to list" link.
