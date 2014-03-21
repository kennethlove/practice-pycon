from django.db.models import Count
from django.shortcuts import redirect
from django.views import generic

from braces import views

from . import forms
from . import models


class RestrictToOwnerMixin(views.LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class TalkListListView(
    RestrictToOwnerMixin,
    generic.ListView
):
    model = models.TalkList

    def get_queryset(self):
        queryset = super(TalkListListView, self).get_queryset()
        queryset = queryset.annotate(talk_count=Count('talks'))
        return queryset


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
