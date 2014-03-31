from django.contrib import messages
from django.db.models import Count
from django.http import Http404
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


class TalkListScheduleView(
    RestrictToOwnerMixin,
    views.PrefetchRelatedMixin,
    generic.DetailView
):
    model = models.TalkList
    prefetch_related = ('talks',)
    template_name = 'talks/schedule.html'


class TalkListRemoveTalkView(generic.RedirectView):
    model = models.Talk

    def get_redirect_url(self, *args, **kwargs):
        return self.talklist.get_absolute_url()

    def get_object(self, pk, talklist_pk):
        try:
            talk = self.model.objects.get(
                pk=pk,
                talk_list_id=talklist_pk
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


class TalkDetailView(views.LoginRequiredMixin, generic.DetailView):
    http_method_names = ['get', 'post']
    form_class = forms.TalkRatingForm
    model = models.Talk

    def get_queryset(self):
        return self.model.objects.filter(talk_list__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TalkDetailView, self).get_context_data(**kwargs)
        obj = context['object']
        rating_form = self.form_class(self.request.POST or None, instance=obj)
        context.update({'rating_form': rating_form})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
        return redirect(self.object)

