**********
Auth views
**********

``HomeView``
============

Before we start any authentication views, we should probably have a home page. So, let's make one. Our stub, ``pycon/survivalguide/survivalguide/`` doesn't have a ``views.py``, so let's go ahead and create it with ``touch survivalguide/views.py``. Let's create our first view here:

.. code-block:: python

   from django.views import generic


   class HomePageView(generic.TemplateView):
       template_name = 'home.html'


Template
--------

Now we need to ``touch templates/home.html`` and open it up for editing. It'll be a pretty simple view so let's just put the following into it:

.. code-block:: html

    {% extends '_layouts/base.html' %}

    {% block headline %}<h1>Welcome to the PyCon Survival Guide!</h1>{% endblock headline %}

    {% block content %}
    <p>Howdy{% if user.is_authenticated %} {{ user.username }}{% endif %}!</p>
    {% endblock %}


URL
---

Finally, we need an URL so we can reach the view. In ``survivalguide/urls.py``, add the following:

.. code-block:: python

   [...]
   from .views import HomePageView
   [...]

   url('^$', HomePageView.as_view(), name='home'),


Now any time we go to ``/`` on our site, we'll get our template.


``SignUpView``
==============

Now, we need to make a view for users to be able to signup at. Let's update our ``survivalguide/views.py`` file like so:

.. code-block:: python

   from django.contrib.auth.forms import UserCreationForm
   from django.contrib.auth.models import User


   class SignUpView(generic.CreateView):
       form_class = UserCreationForm
       model = User
       template_name = 'accounts/signup.html'


URL
---

Since we want to be able to get to the view from a URL, we should add one to ``survivalguide/urls.py``.

.. code-block:: python

   [...]
   from .views import SignUpView
   [...]

   url(r'^accounts/register/$', SignUpView.as_view(), name='signup'),
   [...]


Template
--------

Since we told the view that the template was in an ``accounts`` directory, we need to make one in our global ``templates`` directory. We have to make this directory because ``accounts`` isn't an app. ``mkdir templates/accounts`` and then ``touch templates/accounts/signup.html``.

``signup.html`` should look like:

.. code-block:: html

    {% extends '_layouts/base.html' %}

    {% block title %}Register | {{ block.super }}{% endblock %}

    {% block headline %}<h1>Register for the PyCon Survival Guide</h1>{% endblock %}

    {% block content %}
        <form action='' method="POST">
            {% csrf_token %}
            {{ form.as_p }}
            <input type="submit" value="Sign Up">
        </form>
    {% endblock %}


This default form doesn't render the most beautiful HTML and, thinking about our future forms, we'll have to do a lot of HTML typing just to make them work. None of this sounds like fun work and we're not using a Python web framework in order to have to write a bunch of HTML, so let's save ourselves some time and trouble by using ``django-crispy-forms``.

``django-crispy-forms``
-----------------------

Like pretty much everything, first we need to install ``django-crispy-forms`` with ``pip install django-crispy-forms``. Then we need to add ``'crispy_forms'`` to ``INSTALLED_APPS`` in our settings file and provide a new setting:

.. code-block:: python

    CRISPY_TEMPLATE_PACK = 'bootstrap3'


We have to tell ``django-crispy-forms`` what set of templates to use to render our forms.

New form
--------

``touch survivalguide/forms.py`` and open it in your editor. We need to create a new, custom form, based off of Django's default ``UserCreationForm``.

.. code-block:: python

    from django.contrib.auth.forms import UserCreationForm

    from crispy_forms.helper import FormHelper
    from crispy_forms.layout import Layout, ButtonHolder, Submit

    class RegistrationForm(UserCreationForm):
        def __init__(self, *args, **kwargs):
            super(RegistrationForm, self).__init__(*args, **kwargs)

            self.helper = FormHelper()
            self.helper.layout = Layout(
                'username',
                'password1',
                'password2',
                ButtonHolder(
                    Submit('register', 'Register', css_class='btn-primary')
                )
            )

View changes
------------

In ``survivalguide/views.py``, we need to change our form import from:

.. code-block:: python

   from django.contrib.auth.forms import UserCreationForm

to

.. code-block:: python

   from .forms import RegistrationForm

Since we're using relative imports, we should add:

.. code-block:: python

   from __future__ import absolute_import

to the top of the file to ensure that our imports work like we want.

Change the ``form_class`` in the view to ``RegistrationForm`` and the view should be done.

Template change
---------------

Finally, in the template, change the ``<form>`` area to be: ``{% crispy form %}`` and load the ``django-crispy-forms`` tags with ``{% load crispy_forms_tags %}`` near the top of the file. If we refresh the page, we should now see a decent looking form that works to sign up our user.

``LogInView``
=============

Most of ``LogInView`` is the same work as ``SignUpView``. Since we know we're going to need a custom form, because we want to use ``django-crispy-forms``, let's start there.


Form
----

Back in ``survivalguide/forms.py``:

.. code-block:: python

    from django.contrib.auth.forms import AuthenticationForm


    class LoginForm(AuthenticationForm):
        def __init__(self, *args, **kwargs):
            super(LoginForm, self).__init__(*args, **kwargs)

            self.helper = FormHelper()
            self.helper.layout = Layout(
                'username',
                'password',
                ButtonHolder(
                    Submit('login', 'Login', css_class='btn-primary')
                )
            )

View
----

Then, we should create a view.

.. code-block:: python

    [...]
    from django.contrib.auth import authenticate, login, logout
    from django.core.urlresolvers import reverse_lazy
    [...]
    from .forms import LoginForm
    [...]

    class LoginView(generic.FormView):
        form_class = LoginForm
        success_url = reverse_lazy('home')
        template_name = 'accounts/login.html'

        def form_valid(self, form):
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None and user.is_active:
                login(self.request, user)
                return super(LoginView, self).form_valid(form)
            else:
                return self.form_invalid(form)

URL
---

In our ``survivalguide/urls.py`` file, we need to add a route to our new login view.

.. code-block:: python

   from .views import LoginView
   [...]
   url(r'^accounts/login/$', LoginView.as_view(), name='login'),
   [...]

Template
--------

And, of course, since we gave our view a template name, we have to make sure the template exists. So, in ``templates/accounts/`` go ahead and touch ``login.html`` and fill the file with:

.. code-block:: html

    {% extends '_layouts/base.html' %}

    {% load crispy_forms_tags %}

    {% block title %}Login | {{ block.super }}{% endblock %}

    {% block headline %}<h1>Login to the PyCon Survival Guide</h1>{% endblock %}

    {% block content %}
    {% crispy form %}
    {% endblock %}


``LogOutView``
==============

We should also provide a quick and easy way for users to log out. Thankfully Django makes this pretty simple and we just need a view and an URL.

View
----

In ``survivalguide/views.py``:

.. code-block:: python

    class LogOutView(generic.RedirectView):
        url = reverse_lazy('home')

        def get(self, request, *args, **kwargs):
            logout(request)
            return super(LogOutView, self).get(request, *args, **kwargs)

URL
---

And in our ``survivalguide/urls.py``, we'll import the new view and create an URL:

.. code-block:: python

   [...]
   from .views import LogOutView
   [...]

   url(r'^accounts/logout/$', LogOutView.as_view(), name='logout'),
   [...]


Global template changes
-----------------------

Finally, though, we should have the ability to see if we're logged in or not, and have some links for logging in, signing up, and logging out. So open up ``templates/_layouts/base.html`` and add the following to the ``.navbar-collapse`` area:

.. code-block:: html

    {% if not user.is_authenticated %}
    <a href="{% url 'signup' %}" class="btn btn-default navbar-btn">Register</a>
    <a href="{% url 'login' %}" class="btn btn-default navbar-btn">Login</a>
    {% else %}
    <a href="{% url 'logout' %}" class="btn btn-default navbar-btn">Logout</a>
    {% endif %}


``django-braces``
=================

Our views are complete and pretty solid but it's a little weird that logged-in users can go to the login view and signup view and that logged-out users can go to the logout view. It would also be nice to send the users messages when something happens. Writing code to do all of these things is easy enough but there are already packages out there that provide this functionality. Namely ``django-braces``.

As usual, install it with ``pip install django-braces``. Since ``braces`` doesn't provide any models or templates, we don't have to add it to ``INSTALLED_APPS``, but, as we want to show messages, we should update our ``base.html`` file to provide a place for them.

Messages
--------

Open up ``templates/_layouts/base.html`` and add:

.. code-block:: html

    {% if messages %}
    <ul class="messages">
        {% for message in messages %}
        <li{% if message.tags %} class="alert alert-{{ message.tags }}"{% endif %}>{{ message }}</li>
        {% endfor %}
    </ul>
    {% endif %}

before the ``.jumbotron`` area. This snippet will show any messages in the session in a way that Bootstrap expects.

Views
-----

Now, back in ``survivalguide/views.py``, we need to import ``django-braces``, so add:

.. code-block:: python

   from braces import views

to the imports area near the top of the file. We need to add a few mixins and attributes to a few of the views, so let's do that now.

``SignUpView``
^^^^^^^^^^^^^^

Add ``views.AnonymousRequiredMixin`` and ``views.FormValidMessageMixin`` to the class's signature. We should also add a ``form_valid_message`` attribute to the class which'll be shown to the user when they have successfully signed up.

The ``AnonymousRequiredMixin`` prevents authenticated users from accessing the view.

``LogInView``
^^^^^^^^^^^^^

Add the same two mixins to this view as well and set a ``form_valid_message`` that tells the user that they're logged in.

``LogOutView``
^^^^^^^^^^^^^^

``LogOutView`` needs the ``views.LoginRequiredMixin`` and the ``views.MessageMixin`` added to it.

The ``LoginRequiredMixin`` prevents this view from being accessed by anonymous users.

We also need to update the ``get`` method on the view and add:

.. code-block:: python

   self.messages.success("You've been logged out. Come back soon!")

to it before the ``super()`` call.

Now all of our views should be properly protected and give useful feedback when they're used.
