import datetime
from django import forms

from leagues.models import League, CedhResult

FORMATS = {
    ('LEG', 'Legacy'),
    ('MOD', 'Modern')
}


class UploadForm(forms.Form):
    file = forms.FileField()
    league = forms.ModelChoiceField(League.objects.all())


class CedhResultForm(forms.ModelForm):
    class Meta:
        model = CedhResult
        fields = ['league', 'player', 'date', 'points']
