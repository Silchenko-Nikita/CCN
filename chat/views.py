from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import ListView

from chat.models import Chat, ChatMessage
from chat.views_mixins import ChatUnreadChatCountMixin


class ChatView(LoginRequiredMixin, ChatUnreadChatCountMixin, DetailView):
    template_name = 'chat.html'
    model = Chat

    def get(self, request, *args, **kwargs):
        chat = self.get_object()
        chat.messages.exclude(author=self.request.user).update(is_read=True)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd['messages'] = self.get_object().messages.order_by('id')
        return cd


class ChatRooms(LoginRequiredMixin, ChatUnreadChatCountMixin, ListView):
    template_name = 'chatrooms.html'
    model = Chat

    def get_queryset(self):
        return Chat.objects.filter(users=self.request.user)

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd['unread_chats'] = Chat.objects.filter(
            messages__in=ChatMessage.objects.filter(~Q(author=self.request.user) & Q(is_read=False),
                                                    chat__users=self.request.user)).distinct()
        return cd


def query_chat_view(request):
    users_ids = request.GET.get('users_ids')
    users = [int(id) for id in users_ids.split(',')] if users_ids else []
    chats = Chat.objects.filter(users__in=users).annotate(num=Count('users')).filter(num=len(users))

    if chats.exists():
        chat = chats.first()
    else:
        chat = Chat.objects.create()
        chat.users.add(*users)

    return HttpResponseRedirect(chat.get_absolute_url())