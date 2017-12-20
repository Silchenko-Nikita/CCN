from django.db.models import Q

from chat.models import Chat, ChatMessage


class ChatUnreadChatCountMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['unread_chats_num'] = Chat.objects.filter(
            messages__in=ChatMessage.objects.filter(~Q(author=self.request.user) & Q(is_read=False),
                                                    chat__users=self.request.user)).distinct().count()
        return context