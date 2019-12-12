from django import forms
from .models import Torrent
from django.core.exceptions import ValidationError

class SearchForm(forms.Form):
    search = forms.CharField(strip=True)

class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea, min_length=110, max_length=300, help_text="300 characters max.")
    
    def clean_comment(self):
        com = self.cleaned_data['comment']
        if len(com) >= 200:
            raise ValidationError('Too many characters. 200 max.')
        return com

    class Meta:
        fields = ('comment')