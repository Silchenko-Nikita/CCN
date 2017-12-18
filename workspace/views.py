import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from general.consts import OBJECT_STATUS_ACTIVE, OBJECT_STATUS_DELETED
from workspace.forms import LiteraryComposForm, LiteraryComposTitleForm
from workspace.models import Compos, ComposCommit, ComposBranch
from workspace.views_mixins import LiteraryComposViewMixin


class WorkspaceHome(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['literary_composes'] = Compos.objects.filter(author=self.request.user,
                                                             status=OBJECT_STATUS_ACTIVE).order_by('-id')
        return context


class LiteraryComposTitleUpdateView(LoginRequiredMixin, LiteraryComposViewMixin, UpdateView):
    model = Compos
    context_object_name = 'compos'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        compos = self.get_object()
        form = LiteraryComposTitleForm(instance=compos, data=request.POST or {})
        if form.is_valid():
            form.save()

        commit_id = int(self.kwargs.get('commit_id'))
        if commit_id:
            return redirect(reverse('literary-compos-commit', kwargs={'compos_id': int(self.kwargs.get('compos_id')),
                                                          'branch_id': int(self.kwargs.get('branch_id')),
                                                          'commit_id': commit_id}))
        else:
            return redirect(reverse('literary-compos', kwargs={'compos_id': int(self.kwargs.get('compos_id'))}))


class LiteraryComposDeleteView(LoginRequiredMixin, LiteraryComposViewMixin, UpdateView):
    template_name = 'lit_compos/edit.html'
    model = Compos
    context_object_name = 'compos'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        compos = self.get_compos(raise_404=True)

        if self.kwargs.get('commit_id'):
            commit = self.get_commit(raise_404=True)
            commit.mark_deleted()

            parent = commit.parent
            if parent:
                return redirect(
                    reverse('literary-compos-commit', kwargs={'compos_id': int(self.kwargs.get('compos_id')),
                                                              'branch_id': parent.branch.branch_id,
                                                              'commit_id': parent.commit_id}))
            else:
                return redirect(reverse('literary-compos', kwargs={'compos_id': int(self.kwargs.get('compos_id'))}))
        else:
            compos.mark_deleted()
            return redirect(reverse('workspace-home'))


class LiteraryComposView(LoginRequiredMixin, LiteraryComposViewMixin, DetailView):
    template_name = 'lit_compos/edit.html'

    def post(self, request, *args, **kwargs):
        update_commit = request.GET.get('update_commit')

        commit = self.get_commit()
        form = LiteraryComposForm(request.POST or None, instance=commit)
        if form.is_valid():
            commit = form.commit(branch=self.get_branch(), amend=True) if update_commit else\
                form.commit(branch=self.get_branch())
        return redirect(commit.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_guest'] = False
        return context


class WorkspaceGuest(LoginRequiredMixin, TemplateView):
    template_name = 'guest.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['literary_composes'] = Compos.objects.filter(author_id=self.kwargs.get('author_id'),
                                                             status=OBJECT_STATUS_ACTIVE).order_by('-id')
        return context


class LiteraryComposGuestView(LoginRequiredMixin, LiteraryComposViewMixin, DetailView):
    template_name = 'lit_compos/preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_guest'] = True
        return context


def new_literary_compos_view(request):
    compos = Compos.objects.create(title=None, author=request.user)
    return HttpResponseRedirect(compos.get_absolute_url())