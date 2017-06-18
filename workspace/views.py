from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import TemplateView

from workspace.forms import LiteraryComposBranchForm
from workspace.models import LiteraryCompos, LiteraryComposBranch


class WorkspaceHome(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['literary_composes'] = LiteraryCompos.objects.filter(author=self.request.user)
        return context


class LiteraryComposBranchView(LoginRequiredMixin, DetailView):
    template_name = 'lit_compos/edit.html'
    model = LiteraryComposBranch
    context_object_name = 'compos'
    pk_url_kwarg = 'branch_pk'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compos_br = get_object_or_404(LiteraryComposBranch, id=self.kwargs['branch_pk'])
        context['form'] = LiteraryComposBranchForm(instance=compos_br)
        return context

    def post(self, request, pk, branch_pk, *args, **kwargs):
        compos_br = get_object_or_404(LiteraryComposBranch, id=branch_pk)
        form = LiteraryComposBranchForm(request.POST or None, instance=compos_br)
        if form.is_valid:
            form.save()
        return redirect(compos_br.get_view_url)


def new_literary_compos_view(request):
    br = LiteraryComposBranch.objects.create(author=request.user)
    compos = LiteraryCompos.objects.create(author=request.user, master=br)
    return HttpResponseRedirect(compos.get_view_url)