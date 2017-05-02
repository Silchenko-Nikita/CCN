from django.shortcuts import render
from django.views.generic import DetailView


class ChatView(DetailView):
    template_name = 'chat.html'
    # model = Ch