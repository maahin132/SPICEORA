from django.contrib import admin
from django.utils.html import format_html

from .models import (
    CropSeason,
    ExportEnquiry,
    Farm,
    Harvest,
    InventoryMovement,
    ProcessingRecord,
    Product,
    ProductCategory,
    ProductionBatch,
)


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


class HistoricalAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return False


class CropSeasonInline(admin.TabularInline):
    model = CropSeason
    extra = 0
    fields = ("reference", "crop_name", "planting_date", "status")
    show_change_link = True
    can_delete = False


class HarvestInline(admin.TabularInline):
    model = Harvest
    extra = 0
    fields = ("reference", "harvest_date", "quantity", "quantity_unit")
    show_change_link = True
    can_delete = False


class ProductionBatchInline(admin.TabularInline):
    model = ProductionBatch
    extra = 0
    fields = ("reference", "product_name", "batch_date", "status")
    show_change_link = True
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        return ("reference", "product_name", "batch_date", "status") if obj else ()

    def has_add_permission(self, request, obj=None):
        return False


class ProcessingRecordInline(admin.TabularInline):
    model = ProcessingRecord
    extra = 0
    fields = (
        "activity",
        "activity_date",
        "input_quantity",
        "input_unit",
        "output_quantity",
        "output_unit",
    )
    show_change_link = True
    can_delete = False


class InventoryMovementInline(admin.TabularInline):
    model = InventoryMovement
    extra = 0
    fields = (
        "reference",
        "movement_type",
        "quantity",
        "quantity_unit",
        "movement_date",
        "reason",
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Farm)
class FarmAdmin(HistoricalAdmin):
    list_display = ("reference", "name", "location_summary", "area", "area_unit", "is_active")
    list_filter = ("is_active", "area_unit")
    search_fields = ("reference", "name", "location")
    list_editable = ("is_active",)
    inlines = (CropSeasonInline,)
    fieldsets = (
        ("Farm record", {"fields": ("reference", "name", "location")}),
        ("Area (optional)", {"fields": ("area", "area_unit")}),
        ("Internal information", {"fields": ("description", "internal_notes")}),
        ("Status and history", {"fields": ("is_active", "created_at", "updated_at")}),
    )

    @admin.display(description="Location")
    def location_summary(self, farm):
        return farm.location[:80]


@admin.register(CropSeason)
class CropSeasonAdmin(HistoricalAdmin):
    list_display = (
        "reference",
        "farm",
        "crop_name",
        "planting_date",
        "expected_harvest_date",
        "status",
    )
    list_filter = ("status", "farm")
    search_fields = ("reference", "crop_name", "farm__reference", "farm__name")
    inlines = (HarvestInline,)
    fieldsets = (
        ("Season and farm", {"fields": ("reference", "farm", "crop_name", "status")}),
        ("Dates", {"fields": ("planting_date", "expected_harvest_date")}),
        ("Internal notes", {"fields": ("internal_notes",)}),
        ("History", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Harvest)
class HarvestAdmin(HistoricalAdmin):
    list_display = (
        "reference",
        "crop_season",
        "farm_reference",
        "harvest_date",
        "quantity",
        "quantity_unit",
    )
    list_filter = ("quantity_unit", "harvest_date")
    search_fields = (
        "reference",
        "crop_season__reference",
        "crop_season__crop_name",
        "crop_season__farm__reference",
    )
    inlines = (ProductionBatchInline,)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Harvest", {"fields": ("reference", "crop_season", "harvest_date")}),
        ("Quantity", {"fields": ("quantity", "quantity_unit")}),
        ("Notes", {"fields": ("notes",)}),
        ("History", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Farm reference")
    def farm_reference(self, harvest):
        return harvest.crop_season.farm.reference


@admin.register(ProductionBatch)
class ProductionBatchAdmin(HistoricalAdmin):
    list_display = (
        "reference",
        "product_name",
        "harvest",
        "season_reference",
        "farm_reference",
        "batch_date",
        "status",
        "available_quantity_kg",
    )
    list_filter = ("status", "batch_date")
    search_fields = (
        "reference",
        "product_name",
        "harvest__reference",
        "harvest__crop_season__reference",
        "harvest__crop_season__farm__reference",
    )
    inlines = (ProcessingRecordInline, InventoryMovementInline)
    fieldsets = (
        ("Batch and traceability", {"fields": ("reference", "harvest", "product_name")}),
        ("Initial production", {"fields": ("batch_date", "initial_quantity", "quantity_unit")}),
        ("Current handling", {"fields": ("status", "internal_notes")}),
        ("Inventory", {"fields": ("available_quantity_kg",)}),
        ("History", {"fields": ("created_at", "updated_at")}),
    )

    def get_readonly_fields(self, request, obj=None):
        historical_fields = (
            "created_at",
            "updated_at",
            "available_quantity_kg",
        )
        if obj:
            return historical_fields + (
                "reference",
                "harvest",
                "product_name",
                "batch_date",
                "initial_quantity",
                "quantity_unit",
            )
        return historical_fields

    @admin.display(description="Season")
    def season_reference(self, batch):
        return batch.harvest.crop_season.reference

    @admin.display(description="Farm")
    def farm_reference(self, batch):
        return batch.harvest.crop_season.farm.reference

    @admin.display(description="Available (kg)")
    def available_quantity_kg(self, batch):
        from .models import inventory_balances

        on_hand, reserved = inventory_balances(batch)
        return on_hand - reserved


@admin.register(ProcessingRecord)
class ProcessingRecordAdmin(HistoricalAdmin):
    list_display = ("batch", "activity", "activity_date", "input_quantity", "output_quantity")
    list_filter = ("activity_date",)
    search_fields = ("batch__reference", "batch__product_name", "activity")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "activity_date"

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "batch",
        "movement_type",
        "quantity",
        "quantity_unit",
        "movement_date",
        "reason",
    )
    list_filter = ("movement_type", "movement_date")
    search_fields = ("reference", "batch__reference", "reason")
    readonly_fields = ("created_at",)
    date_hierarchy = "movement_date"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.has_perm("api.approve_inventory_correction"):
            field = form.base_fields.get("movement_type")
            if field:
                field.choices = tuple(
                    choice
                    for choice in field.choices
                    if choice[0]
                    not in {
                        InventoryMovement.MovementType.CORRECTION_IN,
                        InventoryMovement.MovementType.CORRECTION_OUT,
                    }
                )
        return form

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
