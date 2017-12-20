from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext as _
from general.models import CreatedUpdatedModel


class Chat(CreatedUpdatedModel):
    users = models.ManyToManyField(User, related_name='chats')
    name = models.CharField(max_length=512, default=None, null=True, blank=True)

    def __str__(self):
        return (str(self.name) + " chat") if self.name else ', '.join([str(user) for user in self.users.all()]) + " chat"

    class Meta:
        db_table = 'chat'
        verbose_name = _('Chat')
        verbose_name_plural = _('Chats')

    def get_absolute_url(self):
        return reverse('chat', kwargs={'pk': self.id})


class ChatMessage(CreatedUpdatedModel):
    chat = models.ForeignKey(Chat, related_name='messages')
    author = models.ForeignKey(User, related_name='messages')
    text = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'chat_message'
        verbose_name = _('Chat message')
        verbose_name_plural = _('Chat messages')