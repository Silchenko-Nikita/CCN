from django.conf.urls import url

from chat.views import ChatView, query_chat_view, ChatRooms

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', ChatView.as_view(), name="chat"),
    url(r'^list/$', ChatRooms.as_view(), name="chatrooms"),
    url(r'^query/$', query_chat_view, name="new-chat"),
]
