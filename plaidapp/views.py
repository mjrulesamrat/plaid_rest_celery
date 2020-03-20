from django.conf import settings

from rest_framework import permissions
from rest_framework.generics import CreateAPIView, ListAPIView
from plaid import Client


class ObtainAccessTokenView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        client = Client(
            client_id=settings.PLAID_CLIENT_ID,
            secret=settings.PLAID_SECRET,
            public_key=settings.PLAID_PUBLIC_KEY,
            environment=settings.PLAID_ENV
        )
        # create model and store access_token, item_id, request_id


class TransactionListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    # define serializer for transactions data

    def get_queryset(self):
        pass
