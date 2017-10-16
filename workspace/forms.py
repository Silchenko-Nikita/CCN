from django.forms import ModelForm, CharField, Textarea
from django.utils.translation import ugettext as _

from workspace.models import ComposCommit


class LiteraryComposForm(ModelForm):
    content = CharField(widget=Textarea, required=False)

    class Meta:
        model = ComposCommit
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({'placeholder': _('Title')})

        self.fields['content'].widget.attrs.update({'style': 'height: 400px', 'placeholder': _('Composition')})
        self.fields['content'].initial = self.instance.get_content()

    def commit(self, branch=None):
        if self.is_valid():
            if not self.instance.pk:
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
