import datetime
from django import forms

from .models import League, CedhResult, Player

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
        fields = ['league', 'player', 'date', 'points', 'played_both']


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['dci', 'first', 'last', 'nickname']


class NewLeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ['format', 'date_started', 'number_of_events']
