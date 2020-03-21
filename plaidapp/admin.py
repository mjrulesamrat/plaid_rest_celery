from django.contrib import admin

from .models import PlaidItem, ItemMetaData, Account, Balance, Transaction


class PlaidItemAdmin(admin.ModelAdmin):
    list_display = ("identifier", "user", "modified")


class ItemMetaAdmin(admin.ModelAdmin):
    list_display = (
        "identifier", "item_id",
        "last_successful_update", "webhook_last_code_sent"
    )


class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "identifier", "account_id", "name"
    )


class BalanceAdmin(admin.ModelAdmin):
    list_display = (
        "id", "current", "available", "iso_currency_code"
    )


class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id", "transaction_type", "amount", "date"
    )


admin.site.register(PlaidItem, PlaidItemAdmin)
admin.site.register(ItemMetaData, ItemMetaAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transaction, TransactionAdmin)
