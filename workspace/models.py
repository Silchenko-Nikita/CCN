from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from redactor.fields import RedactorField
from simple_history.models import HistoricalRecords

from general.models import CreatedUpdatedModel


class HistLiteraryComposBranchBase(models.Model):
    child_branches = models.ManyToManyField('LiteraryComposBranch', related_name='parents')

    class Meta:
        abstract = True


class LiteraryCompos(CreatedUpdatedModel):
    title = models.CharField(max_length=512)
    author = models.ForeignKey(User, related_name='literary_composes')
    master = models.OneToOneField('LiteraryComposBranch')

    @property
    def get_view_url(self):
        return reverse('literary-compos', kwargs={'pk': self.id, 'branch_pk': self.master.id})


class LiteraryComposBranch(CreatedUpdatedModel):
    author = models.ForeignKey(User, related_name='literary_composes_branches')
    changed_by = models.ForeignKey(User, related_name='changed_literary_composes_branches', null=True, blank=True)
    title = models.CharField(max_length=512)
    content = RedactorField()
    history = HistoricalRecords(bases=[HistLiteraryComposBranchBase])

    @property
    def get_view_url(self):
        return reverse('literary-compos', kwargs={'pk': self.author.id, 'branch_pk': self.id})

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value


# @receiver(post_save, sender=LiteraryCompos)
# def create_master(sender, instance, created, **kwargs):
#     if created:
#         LiteraryComposBranch.objects.create(literary_compos=instance)
