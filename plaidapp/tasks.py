from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

import structlog
from plaid.errors import APIError, RateLimitExceededError, PlaidError

from plaid_rest_celery.celery import plaid_app
from .utils import get_plaid_client
from .models import PlaidItem, ItemMetaData, Account, Balance

celery_logger = structlog.get_logger("celery")

User = get_user_model()


# BTW bind=True is helpful to restart this task in case it is failed
@plaid_app.task(
    bind=True,
    default_retry_delay=60*1,
    max_retries=2
)
def fetch_item_metadata(self, user_id, item_uuid):
    """
    Fetches newly created item's meta data and stores in database
    """
    client = get_plaid_client()
    user = User.objects.get(pk=user_id)
    try:
        item = PlaidItem.objects.get(identifier=item_uuid)
        item_response = client.Item.get(item.access_token)
        item_data = item_response["item"]
        status_data = item_response["status"]

        item_meta_data_obj = ItemMetaData(
            user=user,
            item=item,
            available_products=", ".join(item_data.get("available_products")),
            billed_products=", ".join(item_data.get("billed_products")),
            item_meta_id=item_data.get("item_id"),
            institution_id=item_data.get("institution_id"),
            webhook=item_data.get("webhook", ""),
            last_successful_update=status_data.get("last_successful_update"),
            last_failed_update=status_data.get("last_failed_update"),
        )

        if status_data.get("last_webhook"):
            item_meta_data_obj.webhook_last_sent_at = status_data["last_webhook"]["sent_at"]
            item_meta_data_obj.webhook_last_code_sent = status_data["last_webhook"]["code_sent"]

        item_meta_data_obj.save()

        celery_logger.info(
            "fetch_item_metadata success",
            plaid_request_id=item_response['request_id'],
            fetch_item="success"
        )
        return "Fetch Item meta-data success"
    except PlaidError as exc:
        # logging error
        celery_logger.info(
            exc.display_message,
            token_exchange="fail",
            error_type=exc.type,
            error_code=exc.code,
            plaid_request_id=exc.request_id
        )

        # now, Scope is very wide. Handling few errors only due to time constraint
        # Also, we can define another task which takes care of notifications
        # Also, identifying an error can become a long running task itself!
        if exc.type == "ITEM_ERROR" and exc.code == "ITEM_LOGIN_REQUIRED":
            # No need to retry as customer need to re-authenticate via
            # Link's update mode
            # Log error and notify notification system to send an e-mail
            pass
            return "No ItemMeta stored!"

        if exc.type == "RATE_LIMIT_EXCEEDED" and exc.code == "ITEM_GET_LIMIT":
            # cool down for X minutes and try again
            pass
            raise self.retry(countdown=60*5, exc=exc)

        # default Retry in 1 minutes.
        raise self.retry(countdown=60 * 1, exc=exc,)


@plaid_app.task(bind=True, max_retries=3)
def fetch_accounts_data(self, user_id, item_uuid):
    """
    Fetches item's accounts and stores in db
    """
    client = get_plaid_client()
    user = User.objects.get(pk=user_id)
    try:
        item = PlaidItem.objects.get(identifier=item_uuid)

        accounts_response = client.Accounts.get(item.access_token)
        for account in accounts_response["accounts"]:
            account_obj = Account(
                user=user,
                item=item,
                account_id=account["account_id"],
                mask=account["mask"],
                name=account["name"],
                official_name=account["official_name"],
                type=account.get("type", ""),
                subtype=account.get("subtype", "")
            )
            account_obj.save()

            balance_data = account["balances"]
            balance_obj = Balance(
                current=balance_data["current"],
                available=balance_data.get("available", ""),
                limit=balance_data.get("limit"),
                iso_currency_code=balance_data["iso_currency_code"],
                unofficial_currency_code=balance_data.get("unofficial_currency_code", "")
            )
            balance_obj.save()

        # Log event
        celery_logger.info(
            "fetch_accounts_data success",
            plaid_request_id=accounts_response['request_id'],
            fetch_accounts="success"
        )
        return "Fetch account data success"
    except PlaidError as exc:
        celery_logger.info(
            exc.display_message,
            token_exchange="fail",
            error_type=exc.type,
            error_code=exc.code,
            plaid_request_id=exc.request_id
        )
        # Retry in 5 minutes.
        raise self.retry(countdown=60*5, exc=exc)


@plaid_app.task(bind=True, max_retries=5)
def fetch_transactions(self, item_uuid):
    """
    Fetches different accounts transactions and stores in db

    Making separate calls for different accounts can reduce time running this task
    """
    client = get_plaid_client()
    start_date = '{:%Y-%m-%d}'.format(timezone.now() + timedelta(-30))
    end_date = '{:%Y-%m-%d}'.format(timezone.now())
    try:
        item = PlaidItem.objects.get(identifier=item_uuid)
        transactions_response = client.Transactions.get(
            item.access_token, start_date, end_date
        )

    except PlaidError as exc:
        celery_logger.info(
            exc.display_message,
            token_exchange="fail",
            error_type=exc.type,
            error_code=exc.code,
            plaid_request_id=exc.request_id
        )
        raise self.retry(countdown=60*4, exc=exc)
