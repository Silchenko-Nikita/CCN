import json

import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.urls import reverse
from django.utils.translation import ugettext as _
from git import Repo

from CCN.settings import MEDIA_ROOT, COMPOSES_DIR
from general.models import CreatedUpdatedModel
from workspace.consts import INITIAL_COMMIT_M, CONTENT_FILE, METADATA_FILE
from workspace.managers import ComposBranchManager, ComposCommitManager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Compos(CreatedUpdatedModel):
    title = models.CharField(blank=True, null=True, max_length=512)
    tag = models.CharField(null=True, blank=True, max_length=512)
    compos_id = models.IntegerField(default=0)  # relates to author
    author = models.ForeignKey(User, related_name='composes')

    def __str__(self):
        return self.title or _('Composition {}').format(self.id)

    def get_absolute_url(self):
        return reverse('literary-compos', kwargs={'compos_id': self.id})

    def get_master_br(self):
        return self.branches.order_by('branch_id').first()

    def get_tree(self):
        master_br = self.get_master_br()
        return master_br.get_tree()

    @property
    def get_repo_name(self):
        return '{}|{}|{}|{}'.format(self.id, self.created.isoformat(), self.author, self.title)

    @property
    def get_repo_path(self):
        full_path = os.path.join(MEDIA_ROOT, COMPOSES_DIR, self.get_repo_name)
        # rel_path = os.path.realpath(full_path, BASE_DIR)
        return full_path

    @property
    def get_default_title(self):
        return 'Composition {}'.format(self.compos_id)

    def repo_exists(self):
        return os.path.exists(self.get_repo_path)

    def save(self, **kwargs):
        created = self.pk is None

        if created:
            self.compos_id = (self.author.composes.aggregate(Max('compos_id'))['compos_id__max'] or 0) + 1

        self.title = self.title or self.get_default_title
        compos = super().save(**kwargs)

        if created:
            br = ComposBranch.objects.create(author=self.author,
                                             title=self.title, compos=self, content=getattr(self, 'content', None))
        return compos

    class Meta:
        unique_together = (('compos_id', 'author'), ('tag', 'author'))


class ComposBranch(CreatedUpdatedModel):
    branch_id = models.IntegerField(default=0)  # relates to compos
    tag = models.CharField(null=True, blank=True, max_length=512)
    author = models.ForeignKey(User)
    parent_commit = models.ForeignKey('ComposCommit', related_name='child_branches', null=True, blank=True)
    compos = models.ForeignKey(Compos, related_name='branches')
    objects = ComposBranchManager()

    def get_absolute_url(self):
        return reverse('literary-compos-branch', kwargs={'compos_id': self.compos.id,
                                                'branch_id': self.branch_id})

    def get_last_commit(self):
        return self.commits.order_by('commit_id').last()

    # last commit
    def get_content(self):
        repo = Repo(self.compos.get_repo_path)

        repo.heads[self.get_branch_name].checkout()
        content_path = os.path.join(self.get_repo_path, CONTENT_FILE)
        with open(content_path, 'r') as f:
            content = f.read()

        del repo
        return content

    def get_tree(self):
        first_commit = self.commits.order_by('commit_id').first()
        return first_commit.get_tree()

    @property
    def get_branch_name(self):
        return 'branch_%d' % self.branch_id

    def _commit(self):
        return ComposCommit.objects.create(title=getattr(self, 'title', ''),
                                           content=getattr(self, 'content', ''),
                                           branch=self)

    def save(self, commit=False, **kwargs):
        if not self.pk:
            self.branch_id = (self.compos.branches.aggregate(Max('branch_id'))['branch_id__max'] or 0) + 1

        br = super().save(**kwargs)

        if commit:
            self._commit()

        return br

    class Meta:
        unique_together = (('branch_id', 'compos'), ('tag', 'compos'))


class ComposCommit(CreatedUpdatedModel):
    commit_id = models.IntegerField(default=0)  # relates to branch
    tag = models.CharField(null=True, blank=True, max_length=512)
    title = models.CharField(null=True, blank=True, max_length=512)
    branch = models.ForeignKey(ComposBranch, related_name='commits')
    parent = models.ForeignKey('ComposCommit', related_name='children', null=True, blank=True)
    objects = ComposCommitManager()

    def get_absolute_url(self):
        return reverse('literary-compos-commit', kwargs={'compos_id': self.compos.id,
                                                'branch_id': self.branch_id,
                                                'commit_id': self.commit_id})

    @classmethod
    def get_children_tree(cls, id):
        children = ComposCommit.objects.filter(parent_id=id)
        children_data = children.values('id', 'title', 'tag', 'branch_id', 'commit_id')

        children_res = []
        for data in children_data:
            tree = cls.get_children_tree(id)
            data['children'] = tree
            children_res.append(data)

        return children_res

    def get_tree(self):
        self_data = ComposCommit.objects.filter(id=self.id).values('id', 'title', 'tag', 'branch_id', 'commit_id')[0]
        self_data['children'] = self.get_children_tree(self.id)
        return self_data

    def get_content(self):
        repo_path = self.branch.compos.get_repo_path
        repo = Repo(repo_path)

        repo.git.checkout(self.get_commit_name)
        content_path = os.path.join(repo_path, CONTENT_FILE)
        with open(content_path, 'r') as f:
            content = f.read()

        del repo
        return content

    def checkout(self, author, title, content):
        return ComposBranch.objects.create(author=author, title=title, compos=self.branch.compos, content=content)

    @property
    def get_commit_name(self):
        return '{}|commit_{}'.format(self.branch.get_branch_name, self.commit_id)

    def _commit(self):
        content = getattr(self, 'content', '')

        repo_path = self.branch.compos.get_repo_path
        repo_exists = self.branch.compos.repo_exists()

        br = self.branch

        if not repo_exists:
            repo = Repo.init(repo_path)
            repo.head.rename(br.get_branch_name)

            message = INITIAL_COMMIT_M
        else:
            repo = Repo(repo_path)
            repo.git.checkout('HEAD', b=br.get_branch_name)

            message = 'message'

        content_path = os.path.join(repo_path, CONTENT_FILE)
        with open(content_path, 'w') as f:
            f.write(content or '')

        metadata_path = os.path.join(repo_path, METADATA_FILE)
        data = {
            'author': str(br.author),
            'title': self.title
        }
        with open(metadata_path, 'w') as f:
            json.dump(data, f)

        repo.index.add([CONTENT_FILE, METADATA_FILE])
        repo.index.commit(message)
        repo.create_tag(self.get_commit_name)

        del repo

    def save(self, commit=False, **kwargs):
        last_commit = self.branch.commits.order_by('commit_id').last()
        self.parent = last_commit or self.branch.parent_commit

        if not self.pk:
            self.commit_id = (last_commit.id if last_commit else 0) + 1

        if commit:
            self._commit()

        return super().save(**kwargs)

    class Meta:
        unique_together = (('commit_id', 'branch'), ('tag', 'branch'))
