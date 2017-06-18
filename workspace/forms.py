from django.forms import ModelForm

from workspace.models import LiteraryComposBranch


class LiteraryComposBranchForm(ModelForm):
    class Meta:
        model = LiteraryComposBranch
        fields = ('title', 'content',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'placeholder': 'Title'})
        self.fields['content'].widget.attrs.update({'style': 'height: 400px', 'placeholder': 'Composition'})