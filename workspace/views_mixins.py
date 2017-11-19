from django.http import Http404

from workspace.models import Compos


class LiteraryComposViewMixin:
    def get_compos(self, raise_404=True):
        compos_id = int(self.kwargs.get('compos_id', 0))
        compos = Compos.objects.filter(author=self.request.user, compos_id=compos_id).first()

        if raise_404 and not compos:
            raise Http404

        return compos

    def get_object(self, queryset=None):
        return self.get_compos()