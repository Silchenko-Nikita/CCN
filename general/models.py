from django.db import models

from general.consts import OBJECT_STATUS_ACTIVE, OBJECT_STATUS_DELETED


class CreatedUpdatedModel(models.Model):
    STATUS_CHOICES = (
        (OBJECT_STATUS_ACTIVE, 'Active'),
        (OBJECT_STATUS_DELETED, 'Deleted'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=OBJECT_STATUS_ACTIVE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True