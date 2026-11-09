from django.contrib import admin

from payments.models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "status", "amount", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order__id", "liqpay_order_id"]
