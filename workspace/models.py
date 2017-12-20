import json
from distutils.dir_util import copy_tree

import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.urls import reverse
from django.utils.translation import ugettext as _
from git import Actor
from git import Repo

from CCN.settings import MEDIA_ROOT, COMPOSES_DIR
from general.consts import OBJECT_STATUS_DELETED, OBJECT_STATUS_ACTIVE
from general.models import CreatedUpdatedModel
from workspace.consts import CONTENT_FILE, METADATA_FILE, DEFAULT_COMMIT_MESSAGE, DEFAULT_COMPOS_TITLE
from workspace.managers import ComposBranchManager, ComposCommitManager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Compos(CreatedUpdatedModel):
    title = models.CharField(max_length=512, default=_(DEFAULT_COMPOS_TITLE))
    tag = models.CharField(null=True, blank=True, max_length=512)
    compos_id = models.IntegerField(default=0, null=True)  # relates to author
    author = models.ForeignKey(User, related_name='composes')
    is_public = models.BooleanField(default=False)
    origin = models.ForeignKey('self', related_name='copied_composes', null=True, default=None)

    def __str__(self):
        return (_('Composition {}') + ' ({})').format(self.compos_id, self.title)

    def get_absolute_url(self):
        return reverse('literary-compos', kwargs={'compos_id': self.compos_id})

    def get_guest_url(self):
        return reverse('literary-compos-guest', kwargs={'author_id': self.author_id, 'compos_id': self.compos_id})

    def get_master_br(self):
        return self.branches.order_by('branch_id').first()

    def get_tree(self):
        master_br = self.get_master_br()
        return master_br.get_tree()

    def mark_deleted(self):
        self.status = OBJECT_STATUS_DELETED
        self.compos_id = None
        self.save()

    @property
    def get_repo_name(self):
        return '{}|{}|{}'.format(self.id, self.created.isoformat(), self.author)

    @property
    def get_repo_path(self):
        full_path = os.path.join(MEDIA_ROOT, COMPOSES_DIR, self.get_repo_name)
        return full_path

    def repo_exists(self):
        return os.path.exists(self.get_repo_path)

    def copy(self, new_author):
        origin_repo_path = self.get_repo_path
        master_br = self.get_master_br()

        self.origin_id = self.id
        self.pk = None
        self.author = new_author
        self.is_public = False
        self.save(coping=True)

        master_br.copy(self, new_author)

        new_repo_path = self.get_repo_path
        copy_tree(origin_repo_path, new_repo_path)

    def save(self, coping=False, **kwargs):
        created = self.pk is None

        if created:
            self.compos_id = (self.author.composes.all().aggregate(Max('compos_id'))['compos_id__max'] or 0) + 1

        self.title = self.title or _(DEFAULT_COMPOS_TITLE)
        compos = super().save(**kwargs)

        if created and not coping:
            br = ComposBranch.objects.create(author=self.author,
                                             title=self.title,
                                             compos=self,
                                             content=getattr(self, 'content', None))
        return compos

    class Meta:
        unique_together = (('compos_id', 'author'), ('tag', 'author'))


class ComposBranch(CreatedUpdatedModel):
    branch_id = models.IntegerField(default=0, null=True)  # relates to compos
    tag = models.CharField(null=True, blank=True, max_length=512)
    author = models.ForeignKey(User)
    parent_commit = models.ForeignKey('ComposCommit', related_name='child_branches', null=True, blank=True)
    compos = models.ForeignKey(Compos, related_name='branches')
    objects = ComposBranchManager()

    def mark_deleted(self):
        self.status = OBJECT_STATUS_DELETED
        self.branch_id = None
        self.save()

    def get_absolute_url(self):
        return reverse('literary-compos-branch', kwargs={'compos_id': self.compos.compos_id,
                                                         'branch_id': self.branch_id})

    def get_guest_url(self):
        return reverse('literary-compos-guest-branch', kwargs={'author_id': self.compos.author_id,
                                                               'compos_id': self.compos.compos_id,
                                                               'branch_id': self.branch_id})

    def copy(self, new_compos, new_author):
        first_commit = self.get_first_commit()

        self.pk = None
        self.compos = new_compos
        self.author = new_author
        self.save()

        if first_commit:
            first_commit.copy(self, None)

    def get_last_commit(self):
        return self.commits.filter(status=OBJECT_STATUS_ACTIVE).order_by('commit_id').last()

    def get_first_commit(self):
        return self.commits.filter(status=OBJECT_STATUS_ACTIVE).order_by('commit_id').first()

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
        first_commit = self.get_first_commit()
        return first_commit.get_tree() if first_commit else None

    @property
    def get_branch_name(self):
        return 'branch_{}'.format(self.branch_id)

    def _commit(self):
        return ComposCommit.objects.create(title=getattr(self, 'title', ''),
                                           content=getattr(self, 'content', ''),
                                           compos_title=getattr(self, 'content', DEFAULT_COMPOS_TITLE),
                                           branch=self,
                                           parent=self.parent_commit)

    def save(self, commit=False, **kwargs):
        if not self.pk:
            self.branch_id = (self.compos.branches.filter(status=OBJECT_STATUS_ACTIVE)
                              .aggregate(Max('branch_id'))['branch_id__max'] or 0) + 1

        super().save(**kwargs)

        if commit:
            self._commit()

        return self

    class Meta:
        unique_together = (('id', 'compos'), ('tag', 'compos'))


class ComposCommit(CreatedUpdatedModel):
    commit_id = models.IntegerField(default=0, null=True)  # relates to branch
    tag = models.CharField(null=True, blank=True, max_length=512)
    title = models.CharField(max_length=512)
    commit_message = models.CharField(max_length=128, default=DEFAULT_COMMIT_MESSAGE)
    branch = models.ForeignKey(ComposBranch, related_name='commits')
    parent = models.ForeignKey('ComposCommit', related_name='children', null=True, blank=True)
    objects = ComposCommitManager()
    content = ''

    def copy(self, new_branch, new_parent):
        children = list(self.children.filter().order_by('status', 'branch__branch_id'))
        self.pk = None
        self.branch = new_branch
        self.parent = new_parent
        self.save()

        for commit in children:
            commit.copy(None, self)

    def mark_deleted(self):
        repo = Repo(self.branch.compos.get_repo_path)
        try:
            repo.delete_tag(self.get_commit_name)
        except:
            pass
        del repo

        if self.parent and self.parent.branch_id != self.branch_id:
            self.branch.mark_deleted()

        self.status = OBJECT_STATUS_DELETED
        self.commit_id = None
        self.save()

        for child in self.children.filter(status=OBJECT_STATUS_ACTIVE):
            child.mark_deleted()

    def get_absolute_url(self):
        return reverse('literary-compos-commit', kwargs={'compos_id': self.branch.compos.compos_id,
                                                         'branch_id': self.branch.branch_id,
                                                         'commit_id': self.commit_id})

    @classmethod
    def cls_get_absolute_url(cls, compos_id, branch_id, commit_id):
        return reverse('literary-compos-commit', kwargs={'compos_id': compos_id,
                                                         'branch_id': branch_id,
                                                         'commit_id': commit_id})

    def get_guest_url(self):
        return reverse('literary-compos-guest-commit', kwargs={'author_id': self.branch.compos.author_id,
                                                               'compos_id': self.branch.compos.compos_id,
                                                               'branch_id': self.branch.branch_id,
                                                               'commit_id': self.commit_id})

    @classmethod
    def cls_get_guest_url(cls, author_id, compos_id, branch_id, commit_id):
        return reverse('literary-compos-guest-commit', kwargs={'author_id': author_id,
                                                               'compos_id': compos_id,
                                                               'branch_id': branch_id,
                                                               'commit_id': commit_id})

    @classmethod
    def get_children_tree(cls, id):
        children = ComposCommit.objects.filter(parent_id=id, status=OBJECT_STATUS_ACTIVE)
        children_data = children.values('id', 'title', 'tag', 'commit_message', 'branch__compos__author_id',
                                        'branch__compos__compos_id', 'branch__branch_id', 'commit_id')

        children_res = []
        for data in children_data:
            tree = cls.get_children_tree(data.pop('id'))
            data['children'] = tree
            data['compos_id'] = data.pop('branch__compos__compos_id')
            data['branch_id'] = data.pop('branch__branch_id')
            data['author_id'] = data.pop('branch__compos__author_id')
            data['absolute_url'] = cls.cls_get_absolute_url(data['compos_id'], data['branch_id'], data['commit_id'])
            data['guest_url'] = cls.cls_get_guest_url(data['author_id'], data['compos_id'], data['branch_id'],
                                                      data['commit_id'])
            children_res.append(data)

        return children_res

    def get_tree(self):
        self_data = ComposCommit.objects.filter(id=self.id, status=OBJECT_STATUS_ACTIVE).values(
            'title', 'tag', 'commit_id', 'commit_message',
            'branch__compos__author_id', 'branch__compos__compos_id',
            'branch__branch_id')[0]
        self_data['children'] = self.get_children_tree(self.id)
        compos_id = self_data.pop('branch__compos__compos_id')
        branch_id = self_data.pop('branch__branch_id')
        author_id = self_data.pop('branch__compos__author_id')

        self_data['compos_id'] = compos_id
        self_data['branch_id'] = branch_id
        self_data['author_id'] = author_id
        self_data['absolute_url'] = self.get_absolute_url()
        self_data['guest_url'] = self.get_guest_url()
        return self_data

    def get_content(self):
        if not self.pk:
            return None

        repo_path = self.branch.compos.get_repo_path
        repo_exists = self.branch.compos.repo_exists()
        if not repo_exists:
            return None

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
        br_name = br.get_branch_name

        if not repo_exists:
            repo = Repo.init(repo_path)
            repo.head.rename(br_name)
        else:
            repo = Repo(repo_path)
            repo.git.checkout('-B', br_name)

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

        repo.git.execute(['git', 'config', '--global', 'user.email', '"{}"'.format(br.author.email)])
        repo.git.execute(['git', 'config', '--global', 'user.name', '"{}"'.format(br.author.get_full_name())])

        repo.index.add([CONTENT_FILE, METADATA_FILE])

        if self.pk:
            repo.delete_tag(self.get_commit_name)
            repo.git.commit("-m", "'{}'".format(self.commit_message),
                            "--author='{} <{}>'".format(
                                br.author.get_full_name(), br.author.email), '--amend')
        else:
            author = Actor(br.author.get_full_name(), br.author.email)
            repo.index.commit(self.commit_message, author=author)

        repo.create_tag(self.get_commit_name)

        del repo

    def save(self, coping=False, commit=False, **kwargs):
        if not self.pk:
            if getattr(self, 'parent', None):
                if (not coping and self.parent.children.filter(branch__branch_id=self.parent.branch.branch_id,
                                                               status=OBJECT_STATUS_ACTIVE).exists()) or \
                        (coping and self.parent.children.exists()):
                    br = ComposBranch.objects.create(author=getattr(self, 'author', self.parent.branch.author),
                                                     title=self.title,
                                                     compos=self.parent.branch.compos,
                                                     content=getattr(self, 'content', self.parent.get_content()),
                                                     parent_commit=self.parent)

                    self.branch = br
                else:
                    self.branch = self.parent.branch

            last_commit = self.branch.commits.filter(status=OBJECT_STATUS_ACTIVE).order_by('commit_id').last()
            self.commit_id = (last_commit.commit_id if last_commit else 0) + 1
            self.parent = self.parent or last_commit or self.branch.parent_commit

        if getattr(self, 'compos_title', None):
            self.branch.compos.title = self.compos_title
            self.branch.compos.save()

        if commit:
            self._commit()

        return super().save(**kwargs)

    class Meta:
        unique_together = (('id', 'branch'), ('tag', 'branch'))
