from channels.routing import route, include

from chat.consumers import chat_connect, chat_disconnect, chat_message

chat_routing = [
    route("websocket.connect", chat_connect, path=r"^/(?P<pk>[0-9]+)/$"),
    route("websocket.receive", chat_message, path=r"^/(?P<pk>[0-9]+)/$"),
    route("websocket.disconnect", chat_disconnect, path=r"^/(?P<pk>[0-9]+)/$"),
]

channel_routing = [
    include(chat_routing, path=r"^/chat"),
]