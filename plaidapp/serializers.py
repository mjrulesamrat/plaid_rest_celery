
from rest_framework import serializers

from .models import PlaidItem, Account, Balance, Transaction


class BalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Balance
        fields = (
            'current', 'available', 'limit',
            'iso_currency_code',
            'unofficial_currency_code'
        )


class AccountSerializer(serializers.ModelSerializer):
    balances = BalanceSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = (
            'user', 'identifier',
            'account_id', 'name', 'official_name',
            'type', 'subtype', 'verification_status', 'mask',
            'balances',
        )


class TransactionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = (
            'user',
            'transaction_id', 'account', 'category_id',
            'transaction_type', 'name', 'amount',
            'payment_channel', 'date', 'authorized_date',
            'pending', 'pending_transaction_id',
            'account_owner', 'transaction_code'
        )
