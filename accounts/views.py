from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, login, logout as dj_logout
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from accounts.forms import EmailAuthenticationForm, RegistrationForm, UserProfileInfoForm, AvatarForm
from accounts.models import UserProfile


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['is_owner'] = True
        context['avatar_form'] = AvatarForm()
        context['profile_info_form'] = UserProfileInfoForm(data=model_to_dict(self.request.user.profile))
        return context


class GuestProfileView(LoginRequiredMixin, DetailView):
    template_name = 'profile.html'
    model = User

    def get(self, request, pk, *args, **kwargs):
        if self.request.user == self.get_object():
            return HttpResponseRedirect(reverse_lazy('profile'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        context['is_owner'] = False
        context['profile_info_form'] = UserProfileInfoForm(data=model_to_dict(user.profile))
        return context


class RegisterFormView(FormView):
    form_class = RegistrationForm
    success_url = reverse_lazy('profile')

    template_name = "registration/register.html"

    def form_valid(self, form):
        user = form.save()

        login(self.request, user)
        return super(RegisterFormView, self).form_valid(form)


class UserProfileInfoView(UpdateView):
    form_class = UserProfileInfoForm
    model = UserProfile
    success_url = reverse_lazy('profile')
    template_name = "user_profile_info.html"

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        form.save()

        return super().form_valid(form)


class SearchView(ListView):
    template_name = 'users/list.html'
    model = User
    queryset = User.objects.none()


class FriendsView(ListView):
    template_name = 'users/friends.html'
    model = User
    queryset = User.objects.none()


class InviteToFriends(DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        invited_user = self.get_object()
        request.user.profile.invited_to_friends.add(invited_user.profile)
        return redirect(reverse_lazy('guest-profile', kwargs=self.kwargs))


class ConfirmInvitation(DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        inviter = self.get_object()
        inviter.profile.invited_to_friends.remove(request.user.profile)
        inviter.profile.friends.add(request.user.profile)
        return redirect(reverse_lazy('guest-profile', kwargs=self.kwargs))


class EmailLoginView(LoginView):
    # extra_context = {"next": reverse_lazy("home")}

    form_class = EmailAuthenticationForm


def logout(request):
    dj_logout(request)
    return redirect(reverse_lazy('index'))


class AvatarFormView(LoginRequiredMixin, FormView):
    success_url = reverse_lazy('profile')
    template_name = 'profile.html'
    form_class = AvatarForm

    def form_valid(self, form):
        self.request.user.profile.avatar = form.cleaned_data['avatar']
        self.request.user.profile.save()
        return super().form_valid(form)