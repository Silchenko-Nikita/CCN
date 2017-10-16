from django.conf.urls import url
from workspace.views import LiteraryComposView, WorkspaceHome, new_literary_compos_view

urlpatterns = [
    url(r'^home/$', WorkspaceHome.as_view(), name="workspace-home"),

    url(r'^literary-compos/(?P<compos_id>[0-9]+)/$',
        LiteraryComposView.as_view(),
        name="literary-compos"),

    url(r'^literary-compos/(?P<compos_id>[0-9]+)/branch/(?P<branch_id>[0-9]+)/$',
        LiteraryComposView.as_view(),
        name="literary-compos-branch"),

    url(r'^literary-compos/(?P<compos_id>[0-9]+)/branch/(?P<branch_id>[0-9]+)/commit/(?P<commit_id>[0-9]+)/$',
        LiteraryComposView.as_view(),
        name="literary-compos-commit"),

    url(r'^literary-compos/new/$', new_literary_compos_view, name="literary-compos-new"),
]