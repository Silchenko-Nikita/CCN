from django.conf.urls import url

from chat.views import ChatView

urlpatterns = [
    url(r'^$', ChatView.as_view(), name="chat"),
]