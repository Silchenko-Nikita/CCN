from django.conf.urls import url

from chat.views import ChatView, query_chat_view

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', ChatView.as_view(), name="chat"),
    url(r'^query/$', query_chat_view, name="new-chat"),
]