from django.contrib.auth.models import User
from django.urls import reverse_lazy
from rest_framework import serializers
from rest_framework.fields import ImageField, URLField


class UserSerializer(serializers.HyperlinkedModelSerializer):
    avatar = ImageField(source='profile.avatar')
    profile_view = URLField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['profile_view'] = reverse_lazy('guest-profile', kwargs={"pk": instance.id})
        return ret

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar', 'profile_view',)
        read_only_fields = ('id',)