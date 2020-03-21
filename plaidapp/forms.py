
from django import forms


class PublicTokenForm(forms.Form):
    public_token = forms.CharField(required=True)
