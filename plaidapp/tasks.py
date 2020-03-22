from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

import structlog
from plaid.errors import APIError, RateLimitExceededError, PlaidError

from plaid_rest_celery.celery import plaid_app
from .utils import get_plaid_client
from .models import PlaidItem, ItemMetaData, Account, Balance, Transaction

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
            available_products=", ".join(item_data.get("available_products", "")),
            billed_products=", ".join(item_data.get("billed_products", "")),
            item_meta_id=item_data.get("item_id"),
            institution_id=item_data.get("institution_id"),
            webhook=item_data.get("webhook", None),
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
    except PlaidItem.DoesNotExist as exc:
        # PlaidItem is not created!
        raise self.retry(countdown=10, exc=exc, )
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
            # Handle appropriate filters before using get_or_create
            account_obj = Account(
                user=user,
                item=item,
                account_id=account["account_id"],
                mask=account["mask"],
                name=account["name"],
                official_name=account["official_name"],
                type=account.get("type", None),
                subtype=account.get("subtype", None)
            )
            account_obj.save()

            balance_data = account["balances"]
            balance_obj = Balance(
                account=account_obj,
                current=balance_data["current"],
                available=balance_data.get("available", None),
                limit=balance_data.get("limit"),
                iso_currency_code=balance_data["iso_currency_code"],
                unofficial_currency_code=balance_data.get("unofficial_currency_code", None)
            )
            balance_obj.save()

        # Log event
        celery_logger.info(
            "fetch_accounts_data success",
            plaid_request_id=accounts_response['request_id'],
            fetch_accounts="success"
        )
        return "Fetch account data success"
    except PlaidItem.DoesNotExist as exc:
        # PlaidItem is not created!
        raise self.retry(countdown=10, exc=exc, )
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
def fetch_transactions(self, user_id, item_uuid):
    """
    Fetches different accounts transactions and stores in db

    Making separate calls for different accounts can reduce time running this task
    """
    client = get_plaid_client()
    user = User.objects.get(pk=user_id)
    start_date = '{:%Y-%m-%d}'.format(timezone.now() + timedelta(-30))
    end_date = '{:%Y-%m-%d}'.format(timezone.now())
    try:
        item = PlaidItem.objects.get(identifier=item_uuid)
        transactions_response = client.Transactions.get(item.access_token, start_date, end_date)
        transactions_data = transactions_response["transactions"]
        for transaction in transactions_data:
            account_obj = Account.objects.get(account_id=transaction["account_id"])
            trans_obj = Transaction(
                user=user,
                account=account_obj,
                transaction_id=transaction["transaction_id"],
                category_id=transaction.get("category_id", None),
                transaction_type=transaction["transaction_type"],
                name=transaction["name"],
                amount=transaction["amount"],
                iso_currency_code=transaction.get("iso_currency_code", None),
                unofficial_currency_code=transaction.get("unofficial_currency_code", None),
                date=transaction["date"],
                authorized_date=transaction.get("authorized_date", None),
                payment_channel=transaction["payment_channel"],
                pending=transaction["pending"],
                pending_transaction_id=transaction.get("pending_transaction_id", None),
                account_owner=transaction.get("account_owner", None),
                transaction_code=transaction.get("transaction_code", None),
            )
            trans_obj.save()

        # Log event
        celery_logger.info(
            "fetch_transactions success",
            plaid_request_id=transactions_response['request_id'],
            fetch_transactions="success"
        )
        return "Fetch account data success"

    except PlaidItem.DoesNotExist as exc:
        # PlaidItem is not created!
        raise self.retry(countdown=10, exc=exc, )
    except PlaidError as exc:
        if exc.code == "PRODUCT_NOT_READY":
            # try again after few minutes because transactions data is not ready
            celery_logger.info(
                "fetch_transaction failed",
                token_exchange="fail",
                error_type=exc.type,
                error_code=exc.code,
                plaid_request_id=exc.request_id
            )
            raise self.self.retry(countdown=60*4, exc=exc)

        celery_logger.info(
            exc.display_message,
            token_exchange="fail",
            error_type=exc.type,
            error_code=exc.code,
            plaid_request_id=exc.request_id
        )
        raise self.retry(countdown=60*5, exc=exc)
