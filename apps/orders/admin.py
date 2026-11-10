from django.contrib import admin

from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "total_price", "created_at", "updated_at"]
    list_filter = ["status"]
    search_fields = ["user__email"]
    raw_id_fields = ("user",)
