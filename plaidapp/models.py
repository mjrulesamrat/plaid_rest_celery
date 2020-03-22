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
    # ToDo: Add error jsonfield, ignoring because of sqlite
    identifier = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )
    item = models.ForeignKey(PlaidItem, on_delete=models.CASCADE,)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    item_meta_id = models.CharField(max_length=100)
    institution_id = models.CharField(max_length=100)
    webhook = models.CharField(max_length=256, blank=True, null=True)
    last_successful_update = models.DateTimeField(null=True, blank=True)
    last_failed_update = models.DateTimeField(null=True, blank=True)
    webhook_last_sent_at = models.DateTimeField(null=True, blank=True)
    webhook_last_code_sent = models.CharField(max_length=50, null=True, blank=True)
    billed_products = models.CharField(max_length=200)
    available_products = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Item Metadata"
        verbose_name_plural = "Items Metadata"

    def __str__(self):
        return "%s - %s" % (self.institution_id, self.item)


class Account(TimeStampedModel):
    identifier = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )
    item = models.ForeignKey(PlaidItem, on_delete=models.CASCADE, )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    account_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    official_name = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=30)
    subtype = models.CharField(max_length=30)
    verification_status = models.CharField(max_length=50)
    mask = models.CharField(max_length=10, blank=True, null=True)
    # balance reverse fk

    def __str__(self):
        return "%s - %s - %s" % (self.type, self.user, self.official_name)

    class Meta:
        verbose_name = "Plaid Account"
        verbose_name_plural = "Plaid Accounts"


class Balance(TimeStampedModel):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE,
        related_name="balances"
    )
    current = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Current amount",
    )
    available = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True, null=True,
        verbose_name="Available amount",
    )
    limit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True, null=True,
        verbose_name="Limit",
    )
    iso_currency_code = models.CharField(max_length=10)
    unofficial_currency_code = models.CharField(
        max_length=20, blank=True, null=True
    )

    class Meta:
        verbose_name = "Account Balance"
        verbose_name_plural = "Account Balances"

    def __str__(self):
        return "%s %s" % (self.current, self.iso_currency_code)


class Transaction(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    transaction_id = models.CharField(max_length=50)
    account = models.ForeignKey(Account, on_delete=models.CASCADE,)
    # location
    # category
    category_id = models.CharField(max_length=25)
    transaction_type = models.CharField(max_length=25)
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    iso_currency_code = models.CharField(max_length=10)
    unofficial_currency_code = models.CharField(
        max_length=20, blank=True, null=True
    )
    date = models.DateField()
    authorized_date = models.DateField(null=True, blank=True)
    payment_channel = models.CharField(max_length=50)
    pending = models.BooleanField()
    pending_transaction_id = models.CharField(
        max_length=50, null=True, blank=True
    )
    account_owner = models.CharField(max_length=100, blank=True, null=True)
    transaction_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-date', '-created']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return "%s %s" % (self.name, self.transaction_type)
