import os

from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _

from general.models import CreatedUpdatedModel


User._meta.get_field('email')._unique = True


class UserProfile(CreatedUpdatedModel):
    AVATAR_PATH = os.path.join('accounts', 'avatars')
    DEFAULT_AVATAR = os.path.join(AVATAR_PATH, 'default.png')

    user = models.OneToOneField(User, related_name='profile', unique=True)
    friends = models.ManyToManyField('self', symmetrical=True)
    invited_to_friends = models.ManyToManyField('self', symmetrical=False, related_name='inviters')
    birthday = models.DateField(blank=True, null=True)
    language = models.CharField(max_length=2, choices=LANGUAGES, default='ru')
    about_me = models.TextField(blank=True, null=True)
    avatar = models.ImageField(verbose_name=_('Avatar'), upload_to=AVATAR_PATH, default=DEFAULT_AVATAR)

    def get_absolute_url(self):
        return reverse('guest-profile', kwargs={'pk': self.user.id})

    def __str__(self):
        return str(self.user) + " profile"

    class Meta:
        db_table = 'user_profile'
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)