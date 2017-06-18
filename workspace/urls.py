from django.conf.urls import url
from workspace.views import LiteraryComposBranchView, WorkspaceHome, new_literary_compos_view

urlpatterns = [
    url(r'^home/$', WorkspaceHome.as_view(), name="workspace-home"),
    url(r'^literary-compos/(?P<pk>[0-9]+)/branch/(?P<branch_pk>[0-9]+)/$', LiteraryComposBranchView.as_view(), name="literary-compos"),
    url(r'^literary-compos/new/$', new_literary_compos_view, name="literary-compos-new"),
]