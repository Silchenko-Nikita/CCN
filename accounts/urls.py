from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from accounts.views import ProfileView, SearchView, RegisterFormView, EmailLoginView, GuestProfileView, logout, \
    AvatarFormView, UserProfileInfoView

urlpatterns = [
    url(r'^search/$', SearchView.as_view(), name="profiles-search"),
    url(r'^profile/$', ProfileView.as_view(), name="profile"),
    url(r'^avatar-upload/$', AvatarFormView.as_view(), name="avatar-upload"),
    url(r'^profile-info/$', UserProfileInfoView.as_view(), name="user-profile-info"),
    url(r'^profile/(?P<pk>[0-9]+)/$', GuestProfileView.as_view(), name="guest-profile"),

    url(r'^login/$', EmailLoginView.as_view(), name="login"),
    url(r'^register/$', RegisterFormView.as_view(), name="register"),
    url(r'^logout/$', logout, name="logout"),
]