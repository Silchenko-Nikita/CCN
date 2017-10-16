import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
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

    def get_branch_or_404(self):
        compos = self.get_object()
        branch_id = self.kwargs.get('branch_id')

        if branch_id:
            br = get_object_or_404(ComposBranch, compos=compos, branch_id=branch_id)
        else:
            br = compos.branches.order_by('branch_id').first()
            if not br:
                raise Http404

        return br

    def get_commit_or_404(self, branch_id=None):
        compos = self.get_object()

        if not branch_id:
            br = self.get_branch_or_404()
            branch_id = br.branch_id

        commit_id = self.kwargs.get('commit_id')

        if commit_id:
            commit = get_object_or_404(ComposCommit, compos=compos,
                                   branch__branch_id=branch_id,
                                   commit_id=commit_id)
        else:
            commit = ComposCommit.objects.filter(
                branch__compos=compos,
                branch__branch_id=branch_id).order_by('commit_id').last()
            if not commit:
                raise Http404

        return commit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        br = self.get_branch_or_404()
        commit = self.get_commit_or_404(br.branch_id)
        context['form'] = LiteraryComposForm(instance=commit)
        context['tree'] = mark_safe(json.dumps(br.compos.get_tree()))
        return context

    # def post(self, request, *args, **kwargs):
    #     compos_br = self.branch_or_404()
    #     form = LiteraryComposForm(request.POST or None, instance=compos_br)
    #     if form.is_valid():
    #         form.save()
    #     return redirect(compos_br.get_view_url)


def new_literary_compos_view(request):
    compos = Compos.objects.create(title=None, author=request.user)
    return HttpResponseRedirect(compos.get_absolute_url())