import json

from django.http import Http404
from django.utils.safestring import mark_safe

from general.consts import OBJECT_STATUS_ACTIVE
from workspace.forms import LiteraryComposForm
from workspace.forms import LiteraryComposTitleForm
from workspace.models import Compos, ComposCommit


class LiteraryComposViewMixin:
    model = Compos
    context_object_name = 'compos'

    def get_compos(self, raise_404=True):
        author_id = int(self.kwargs.get('author_id', 0))
        compos_id = int(self.kwargs.get('compos_id', 0))
        compos = Compos.objects.filter(author_id=author_id or self.request.user.id, compos_id=compos_id,
                                       status=OBJECT_STATUS_ACTIVE).first()

        if raise_404 and not compos:
            raise Http404

        return compos

    def get_branch(self, raise_404=True):
        compos = self.get_compos(raise_404=True)
        branch_id = int(self.kwargs.get('branch_id', 0))

        brs = compos.branches.filter(status=OBJECT_STATUS_ACTIVE)
        if branch_id:
            brs = brs.filter(branch_id=branch_id)
            if raise_404 and not brs.exists():
                raise Http404

        br = brs.order_by('branch_id').first()

        return br

    def get_commit(self, raise_404=True):
        br = self.get_branch(raise_404=True)

        commit_id = int(self.kwargs.get('commit_id', 0))

        commits = ComposCommit.objects.filter(branch=br, status=OBJECT_STATUS_ACTIVE)
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

    def get_object(self, queryset=None):
        return self.get_compos()

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user, status=OBJECT_STATUS_ACTIVE)