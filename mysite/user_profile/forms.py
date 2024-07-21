from django import forms
from multiupload.fields import MultiFileField

from .models import Tag


class PostForm(forms.Form):
    content = forms.CharField(
        label='Content',
        widget=forms.Textarea
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        label='Tags',
        widget=forms.SelectMultiple
    )
    post_pictures = MultiFileField(label='Photos')
