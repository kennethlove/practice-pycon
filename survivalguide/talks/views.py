from django.views import generic

from braces import views

from . import forms
from . import models


class RestrictToOwnerMixin(views.LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class TalkListListView(RestrictToOwnerMixin, generic.ListView):
    model = models.TalkList


class TalkListDetailView(RestrictToOwnerMixin, generic.DetailView):
    model = models.TalkList


class TalkListCreateView(generic.CreateView):
    form_class = forms.TalkListForm
    model = models.TalkList

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super(TalkListCreateView, self).form_valid(form)


class TalkListUpdateView(RestrictToOwnerMixin, generic.UpdateView):
    form_class = forms.TalkListForm
    model = models.TalkList
