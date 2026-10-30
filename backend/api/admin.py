from django.contrib import admin
from django.utils.html import format_html

from .models import ExportEnquiry, Product, ProductCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "category",
        "is_published",
        "sort_order",
        "created_at",
        "image_preview",
    )
    list_display_links = ("name", "slug")
    list_editable = ("is_published", "sort_order")
    list_filter = ("is_published", "category")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "image_preview")
    fieldsets = (
        (
            "Product content",
            {"fields": ("name", "slug", "category", "summary", "description")},
        ),
        ("Primary image", {"fields": ("image", "image_alt", "image_preview")}),
        ("Publication", {"fields": ("is_published", "sort_order")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    ordering = ("sort_order", "-created_at")

    @admin.display(description="Image")
    def image_preview(self, product):
        if not product or not product.image:
            return "No image uploaded."
        if not product.image.storage.exists(product.image.name):
            return "Image file is missing."
        return format_html(
            '<img src="{}" alt="" style="max-height: 72px; max-width: 96px; '
            'object-fit: contain;">',
            product.image.url,
        )


@admin.register(ExportEnquiry)
class ExportEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "company_name",
        "email",
        "country",
        "category",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at", "category")
    search_fields = ("full_name", "email", "company_name", "country")
    list_editable = ("status",)
    readonly_fields = ("public_reference", "created_at", "updated_at")
    fieldsets = (
        (
            "Buyer details",
            {
                "fields": (
                    "public_reference",
                    "full_name",
                    "company_name",
                    "email",
                    "phone",
                    "country",
                )
            },
        ),
        (
            "Request",
            {
                "fields": (
                    "category",
                    "product",
                    "product_name_snapshot",
                    "quantity",
                    "quantity_unit",
                    "message",
                )
            },
        ),
        ("Staff handling", {"fields": ("status", "internal_notes")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    actions = None

    def has_add_permission(self, request):
        return False
