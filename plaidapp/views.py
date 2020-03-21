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


logger = structlog.get_logger("plaid")


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
                logger.info(
                    "public-token exchange success",
                    plaid_request_id=exchange_response['request_id'],
                    token_exchange="success"
                )
            except PlaidError as e:
                logger.info(e.display_message,
                            public_token=form.cleaned_data["public_token"],
                            token_exchange="fail",
                            error_type=e.type,
                            error_code=e.code,
                            plaid_request_id=e.request_id)
                data = {"message": e.display_message}
                return Response(data, status=400)

            PlaidItem.objects.create(
                access_token=exchange_response['access_token'],
                item_id=exchange_response['item_id'],
                user=request.user
            )
            logger.info("new item create success",
                        plaid_request_id=exchange_response['request_id'],
                        item_create="success")
            return Response({
                "message": "Account added successfully.",
                "success": True,
            }, status=201)
        else:
            logger.info("invalid public-token provided")
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
