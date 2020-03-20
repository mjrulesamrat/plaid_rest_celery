import uuid

from django.db import models
from django.conf import settings

from django_extensions.db.models import TimeStampedModel


class PlaidItem(TimeStampedModel):
    """
    Each Item has set of credentials and links an unique institute with user
    """
    identifier = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )
    access_token = models.CharField(max_length=200)
    item_id = models.CharField(max_length=200)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Plaid Item"
        verbose_name_plural = "Plaid Items"

    def __str__(self):
        return "%s - %s" % (self.user, self.access_token[-4:])


class ItemMetaData(TimeStampedModel):
    identifier = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )
    item = models.ForeignKey(PlaidItem, on_delete=models.CASCADE,)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    institution_name = models.CharField(max_length=100)
    institution_id = models.CharField(max_length=100)
    webhook = models.CharField(max_length=256)
    last_successful_update = models.DateTimeField(null=True, blank=True)
    last_failed_update = models.DateTimeField(null=True, blank=True)
    webhook_last_sent_at = models.DateTimeField(null=True, blank=True)
    webhook_last_code_sent = models.CharField(max_length=50, null=True, blank=True)
    # billed_products
    # available_products

    class Meta:
        verbose_name = "Item Metadata"
        verbose_name_plural = "Items Metadata"

    def __str__(self):
        return "%s - %s" % (self.institution_id, self.item)


class Account(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )


class Transaction(TimeStampedModel):
    transaction_id = models.CharField(max_length=50)
    account_id = models.CharField(max_length=50)
    # location
    # category
    category_id = models.CharField(max_length=25)
    transaction_type = models.CharField(max_length=25)
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_channel = models.CharField(max_length=50)
    authorized_date = models.DateField(null=True, blank=True)
    date = models.DateField()
    pending = models.BooleanField()
    pending_transaction_id = models.CharField(
        max_length=50, null=True, blank=True
    )
    account_owner = models.CharField(max_length=100, blank=True, null=True)
    transaction_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return self.name
