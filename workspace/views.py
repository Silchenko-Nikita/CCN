import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from chat.views_mixins import ChatUnreadChatCountMixin
from general.consts import OBJECT_STATUS_ACTIVE, OBJECT_STATUS_DELETED
from workspace.forms import LiteraryComposForm, LiteraryComposTitleForm
from workspace.models import Compos, ComposCommit, ComposBranch
from workspace.views_mixins import LiteraryComposViewMixin


class WorkspaceHome(LoginRequiredMixin, ChatUnreadChatCountMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['literary_composes'] = Compos.objects.filter(author=self.request.user,
                                                             status=OBJECT_STATUS_ACTIVE).order_by('-id')
        return context


class LiteraryComposTitleUpdateView(LoginRequiredMixin, ChatUnreadChatCountMixin, LiteraryComposViewMixin, UpdateView):
    model = Compos
    context_object_name = 'compos'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        compos = self.get_object()
        form = LiteraryComposTitleForm(instance=compos, data=request.POST or {})
        if form.is_valid():
            form.save()

        commit = self.get_compos(raise_404=False)
        if commit:
            return redirect(commit.get_absolute_url())
        else:
            return redirect(compos.get_absolute_url())


class LiteraryComposDeleteView(LoginRequiredMixin, ChatUnreadChatCountMixin, LiteraryComposViewMixin, UpdateView):
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
                return redirect(parent.get_absolute_url())
            else:
                return redirect(compos.get_absolute_url())
        else:
            compos.mark_deleted()
            return redirect(reverse('workspace-home'))


class LiteraryComposView(LoginRequiredMixin, ChatUnreadChatCountMixin, LiteraryComposViewMixin, DetailView):
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


class PublishLiteraryComposView(LoginRequiredMixin, ChatUnreadChatCountMixin, View):

    def get_compos(self, raise_404=True):
        compos_id = int(self.kwargs.get('compos_id', 0))
        compos = Compos.objects.filter(author=self.request.user, compos_id=compos_id,
                                       status=OBJECT_STATUS_ACTIVE).first()

        if raise_404 and not compos:
            raise Http404

        return compos

    def get(self, request, *args, **kwargs):
        compos = self.get_compos()
        compos.is_public = True
        compos.save()
        return redirect(reverse('workspace-home'))


class UnpublishLiteraryComposView(LoginRequiredMixin, ChatUnreadChatCountMixin, View):

    def get_compos(self, raise_404=True):
        compos_id = int(self.kwargs.get('compos_id', 0))
        compos = Compos.objects.filter(author=self.request.user, compos_id=compos_id,
                                       status=OBJECT_STATUS_ACTIVE).first()

        if raise_404 and not compos:
            raise Http404

        return compos

    def get(self, request, *args, **kwargs):
        compos = self.get_compos()
        compos.is_public = False
        compos.save()
        return redirect(reverse('workspace-home'))


class WorkspaceGuest(LoginRequiredMixin, ChatUnreadChatCountMixin, TemplateView):
    template_name = 'guest.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['literary_composes'] = Compos.objects.filter(author_id=self.kwargs.get('author_id'),
                                                             is_public=True,
                                                             status=OBJECT_STATUS_ACTIVE).order_by('-id')
        return context


class LiteraryComposGuestView(LoginRequiredMixin, ChatUnreadChatCountMixin, LiteraryComposViewMixin, DetailView):
    template_name = 'lit_compos/preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_guest'] = True
        return context


def new_literary_compos_view(request):
    compos = Compos.objects.create(title=None, author=request.user)
    return HttpResponseRedirect(compos.get_absolute_url())