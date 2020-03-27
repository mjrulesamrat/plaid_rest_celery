
from django import forms


class PublicTokenForm(forms.Form):
    """
    Validations here:
    https://plaid.com/docs/#plaid-tokens-public_token-access_token-or-asset_report_token
    """
    public_token = forms.CharField(required=True)
