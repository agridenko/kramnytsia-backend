from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock", "category", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["name", "description"]
    list_editable = ["price", "stock"]
    prepopulated_fields = {"slug": ("name",)}
