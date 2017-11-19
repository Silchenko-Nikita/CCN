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

from workspace.forms import LiteraryComposForm, LiteraryComposTitleForm
from workspace.models import Compos, ComposCommit, ComposBranch
from workspace.views_mixins import LiteraryComposViewMixin


class WorkspaceHome(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['literary_composes'] = Compos.objects.filter(author=self.request.user)
        return context


class LiteraryComposTitleUpdateView(LoginRequiredMixin, LiteraryComposViewMixin, UpdateView):
    model = Compos
    context_object_name = 'compos'

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


class LiteraryComposView(LoginRequiredMixin, LiteraryComposViewMixin, DetailView):
    template_name = 'lit_compos/edit.html'
    model = Compos
    context_object_name = 'compos'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)

    def get_branch(self, raise_404=True):
        compos = self.get_compos(raise_404=True)
        branch_id = int(self.kwargs.get('branch_id', 0))

        brs = compos.branches.all()
        if branch_id:
            brs = brs.filter(branch_id=branch_id)
            if raise_404 and not brs.exists():
                raise Http404

        br = brs.order_by('branch_id').first()

        return br

    def get_commit(self, raise_404=True):
        br = self.get_branch(raise_404=True)

        commit_id = int(self.kwargs.get('commit_id', 0))

        commits = ComposCommit.objects.filter(branch=br)
        if commit_id:
            commits = commits.filter(commit_id=commit_id)
            if raise_404 and not commits.exists():
                raise Http404

        commit = commits.order_by('commit_id').last()

        return commit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compos = self.get_compos(raise_404=True)
        commit = self.get_commit(raise_404=True)

        if compos:
            context['compos_title_form'] = LiteraryComposTitleForm(instance=compos)
            context['compos_id'] = int(compos.compos_id)

        context['form'] = LiteraryComposForm(instance=commit)
        context['tree'] = mark_safe(json.dumps(compos.get_tree()))

        context['branch_id'] = int(commit.branch.branch_id if commit else self.get_branch(raise_404=True).branch_id)
        context['commit_id'] = int(commit.commit_id if commit else 0)

        context['commit'] = commit
        return context

    def post(self, request, *args, **kwargs):
        update_commit = request.GET.get('update_commit')

        commit = self.get_commit()
        form = LiteraryComposForm(request.POST or None, instance=commit)
        if form.is_valid():
            commit = form.commit(branch=self.get_branch(), amend=True) if update_commit else\
                form.commit(branch=self.get_branch())
        return redirect(commit.get_absolute_url())


def new_literary_compos_view(request):
    compos = Compos.objects.create(title=None, author=request.user)
    return HttpResponseRedirect(compos.get_absolute_url())