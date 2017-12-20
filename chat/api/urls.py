from django.conf.urls import url, include

from chat.api.views import ChatMessagesListView

urlpatterns = [
    url(
        r'^messages$',
        ChatMessagesListView.as_view(),
        name="chat-messages"
    ),
]