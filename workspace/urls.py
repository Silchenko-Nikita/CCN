from django.conf.urls import url
from workspace.views import LiteraryComposView, WorkspaceHome, new_literary_compos_view, LiteraryComposTitleUpdateView, \
    LiteraryComposDeleteView, LiteraryComposGuestView, WorkspaceGuest

urlpatterns = [
    url(r'^$', WorkspaceHome.as_view(), name="workspace-home"),
    url(r'^guest/(?P<author_id>[0-9]+)/$', WorkspaceGuest.as_view(), name="workspace-guest"),

    url(r'^literary-compos/(?P<compos_id>[0-9]+)/$',
        LiteraryComposView.as_view(),
        name="literary-compos"),

    url(r'^literary-compos/(?P<compos_id>[0-9]+)/(?P<branch_id>[0-9]+)/$',
        LiteraryComposView.as_view(),
        name="literary-compos-branch"),

    url(r'^literary-compos/(?P<compos_id>[0-9]+)/(?P<branch_id>[0-9]+)/(?P<commit_id>[0-9]+)/$',
        LiteraryComposView.as_view(),
        name="literary-compos-commit"),

    url(r'^literary-compos/guest/(?P<author_id>[0-9]+)/(?P<compos_id>[0-9]+)/$',
        LiteraryComposGuestView.as_view(),
        name="literary-compos-guest"),

    url(r'^literary-compos/guest/(?P<author_id>[0-9]+)/(?P<compos_id>[0-9]+)/(?P<branch_id>[0-9]+)/$',
        LiteraryComposGuestView.as_view(),
        name="literary-compos-guest-branch"),

    url(r'^literary-compos/guest/(?P<author_id>[0-9]+)/(?P<compos_id>[0-9]+)/(?P<branch_id>[0-9]+)/(?P<commit_id>[0-9]+)/$',
        LiteraryComposGuestView.as_view(),
        name="literary-compos-guest-commit"),

    url(r'^literary-compos/(?P<compos_id>[0-9]+)/delete$',
        LiteraryComposDeleteView.as_view(),
        name="literary-compos-delete"),

    url(r'^literary-compos/(?P<compos_id>[0-9]+)/(?P<branch_id>[0-9]+)/(?P<commit_id>[0-9]+)/update$',
        LiteraryComposTitleUpdateView.as_view(),
        name="literary-compos-update"),

    url(r'^literary-compos/new/$', new_literary_compos_view, name="literary-compos-new"),
]