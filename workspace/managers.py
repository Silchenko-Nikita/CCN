from django.db import models


class ComposBranchManager(models.Manager):

    def create(self, title=None, content=None, compos_title=None, **kwargs):
        obj = self.model(**kwargs)
        self._for_write = True

        obj.title = title
        obj.compos_title = compos_title
        obj.content = content
        obj.save(force_insert=True, using=self.db)
        return obj


class ComposCommitManager(models.Manager):

    def create(self, content=None, compos_title=None, **kwargs):
        obj = self.model(**kwargs)
        self._for_write = True

        obj.content = content
        obj.compos_title = compos_title
        obj.save(commit=True, force_insert=True, using=self.db)
        return obj
