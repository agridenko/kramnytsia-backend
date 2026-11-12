from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    raw_id_fields = ("product",)
    fields = (
        "product",
        "quantity",
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]

    list_display = [
        "id",
        "user",
        "get_total_items",
        "created_at",
        "total_price",
    ]
    list_filter = ["created_at"]
    search_fields = ["user__username", "user__email"]

    @admin.display(description="Кількість товарів")
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
