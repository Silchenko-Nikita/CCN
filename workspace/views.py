import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.safestring import mark_safe
from django.views.generic import DetailView
from django.views.generic import TemplateView

from workspace.forms import LiteraryComposForm
from workspace.models import Compos, ComposCommit, ComposBranch


class WorkspaceHome(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['literary_composes'] = Compos.objects.filter(author=self.request.user)
        return context


class LiteraryComposView(LoginRequiredMixin, DetailView):
    template_name = 'lit_compos/edit.html'
    pk_url_kwarg = 'compos_id'
    model = Compos
    context_object_name = 'compos'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)

    def get_compos(self):
        return self.get_object()

    def get_branch(self):
        compos = self.get_compos()
        branch_id = int(self.kwargs.get('branch_id', 0))

        brs = compos.branches.all()
        if branch_id:
            brs = brs.filter(branch_id=branch_id)

        return brs.order_by('branch_id').first()

    def get_branch_or_404(self):
        compos = self.get_object()
        branch_id = int(self.kwargs.get('branch_id', 0))

        if branch_id:
            br = get_object_or_404(ComposBranch, compos=compos, branch_id=branch_id)
        else:
            br = compos.branches.order_by('branch_id').first()
            if not br:
                raise Http404

        return br

    def get_commit(self):
        br = self.get_branch_or_404()

        commit_id = int(self.kwargs.get('commit_id', 0))

        commits = ComposCommit.objects.filter(branch=br)
        if commit_id:
            commits = commits.filter(commit_id=commit_id)
        commit = commits.order_by('commit_id').last()

        return commit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compos = self.get_compos()
        commit = self.get_commit()

        context['form'] = LiteraryComposForm(instance=commit)
        context['tree'] = mark_safe(json.dumps(compos.get_tree()))
        return context

    def post(self, request, *args, **kwargs):
        commit = self.get_commit()
        form = LiteraryComposForm(request.POST or None, instance=commit)
        if form.is_valid():
            commit = form.commit(branch=self.get_branch())
        return redirect(commit.get_absolute_url())


def new_literary_compos_view(request):
    compos = Compos.objects.create(title=None, author=request.user)
    return HttpResponseRedirect(compos.get_absolute_url())