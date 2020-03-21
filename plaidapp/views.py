import json

from django.conf import settings

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from plaid.errors import PlaidError, InvalidInputError, InvalidRequestError
from plaid import Client
import structlog

from .forms import PublicTokenForm
from .models import PlaidItem
from .tasks import fetch_item_metadata, fetch_accounts_data


plaid_logger = structlog.get_logger("plaid")
celery_logger = structlog.get_logger("celery")


class ObtainAccessTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = [u'post']

    def post(self, request, *args, **kwargs):
        client = Client(
            client_id=settings.PLAID_CLIENT_ID,
            secret=settings.PLAID_SECRET,
            public_key=settings.PLAID_PUBLIC_KEY,
            environment=settings.PLAID_ENV,
            api_version=settings.PLAID_API_VERSION
        )
        form = PublicTokenForm(request.data)
        if form.is_valid():
            try:
                public_token = form.cleaned_data["public_token"]
                exchange_response = client.Item.public_token.exchange(public_token)
                plaid_logger.info(
                    "public-token exchange success",
                    plaid_request_id=exchange_response['request_id'],
                    token_exchange="success"
                )
            except PlaidError as e:
                plaid_logger.info(
                    e.display_message,
                    public_token=form.cleaned_data["public_token"],
                    token_exchange="fail",
                    error_type=e.type,
                    error_code=e.code,
                    plaid_request_id=e.request_id
                )
                data = {"message": e.display_message}
                return Response(data, status=400)

            plaid_item = PlaidItem(
                access_token=exchange_response['access_token'],
                item_id=exchange_response['item_id'],
                user=request.user
            )
            plaid_item.save()

            # add tasks to fetch item metadata and account data
            try:
                fetch_item_metadata.apply_async(plaid_item.identifier)
            except fetch_item_metadata.OperationalError as exc:
                celery_logger.exception('Sending task raised %r', exc)

            plaid_logger.info("new item create success",
                              plaid_request_id=exchange_response['request_id'],
                              item_create="success")
            return Response({
                "message": "Account added successfully.",
                "success": True,
            }, status=201)
        else:
            plaid_logger.info("invalid public-token provided")
            errors = form.errors
            return Response({
                "message": "Validation failed.",
                "errors": errors
            }, status=400)


class TransactionListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = [u'get']
    # define serializer for transactions data

    def get_queryset(self):
        pass
