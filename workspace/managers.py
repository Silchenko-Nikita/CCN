from django.db import models


class ComposBranchManager(models.Manager):

    def create(self, title=None, content=None, **kwargs):
        obj = self.model(**kwargs)
        self._for_write = True

        obj.title = title
        obj.content = content
        obj.save(commit=True, force_insert=True, using=self.db)
        return obj


class ComposCommitManager(models.Manager):

    def create(self, content=None, **kwargs):
        obj = self.model(**kwargs)
        self._for_write = True

        obj.content = content
        obj.save(commit=True, force_insert=True, using=self.db)
        return obj
