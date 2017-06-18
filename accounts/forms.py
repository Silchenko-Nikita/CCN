from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ImageField
from django.utils.translation import ugettext as _

from accounts.models import UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label=_('Email'))
    first_name = forms.CharField(label=_('First name'))
    last_name = forms.CharField(label=_('Last name'))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # username = self.cleaned_data.get('username')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Email addresses must be unique'))
        return email


class EmailAuthenticationForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                no_user = False

                try:
                    user = User.objects.get(email=username)
                    self.user_cache = authenticate(self.request, username=user.username, password=password)
                    if self.user_cache is None:
                        no_user = True
                except ObjectDoesNotExist:
                    no_user = True

                if no_user:
                    raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                        params={'username': self.username_field.verbose_name},
                    )
            else:
                self.confirm_login_allowed(self.user_cache)


class UserProfileInfoForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('birthday', 'language')


class AvatarForm(forms.Form):
    avatar = ImageField(label=_('Avatar'))
