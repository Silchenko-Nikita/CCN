from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView

from chat.models import Chat


class ChatView(LoginRequiredMixin, DetailView):
    template_name = 'chat.html'
    model = Chat


def query_chat_view(request):
    users_ids = request.GET.get('users_ids')
    users = [int(id) for id in users_ids.split(',')] if users_ids else []
    try:
        chat = Chat.objects.filter(users__in=users).annotate(num=Count('users')).filter(num=len(users))[0]
        created = False
    except IndexError:
        chat = Chat.objects.create()
        created = True

    if created:
        chat.users.add(*users)
    return HttpResponseRedirect(reverse('chat', kwargs={ 'pk': chat.id }))