from django.conf import settings

from plaid.client import Client


def get_plaid_client():
    client = Client(
        client_id=settings.PLAID_CLIENT_ID,
        secret=settings.PLAID_SECRET,
        public_key=settings.PLAID_PUBLIC_KEY,
        environment=settings.PLAID_ENV,
        api_version=settings.PLAID_API_VERSION
    )
    return client
