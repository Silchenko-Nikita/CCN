from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, CharField, Textarea
from django.utils.translation import ugettext as _

from workspace.consts import DEFAULT_COMPOS_TITLE
from workspace.models import ComposCommit, Compos


class LiteraryComposForm(ModelForm):
    content = CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = ComposCommit
        fields = ['title', 'commit_message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({'placeholder': _('Title (commit level)')})

        self.fields['commit_message'].widget.attrs.update({'placeholder': _('Commit message')})

        self.fields['content'].widget.attrs.update({'style': 'height: 400px;', 'placeholder': _('Composition')})
        self.fields['content'].initial = self.instance.get_content()

    def commit(self, branch=None, amend=False):
        if self.is_valid():
            if not self.instance.pk or amend:
                self.instance.branch = branch
                self.instance.title = self.cleaned_data['title']
                self.instance.content = self.cleaned_data['content']
                self.instance.save(commit=True)
                return self.instance
            else:
                return ComposCommit.objects.create(title=self.cleaned_data['title'],
                                                   content=self.cleaned_data['content'],
                                                   parent=self.instance,
                                                   branch=branch)


class LiteraryComposTitleForm(ModelForm):
    class Meta:
        model = Compos
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({'placeholder': _('Composition title')})
