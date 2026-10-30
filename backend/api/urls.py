from django.urls import path

from .views import (
    ProductCategoryListView,
    ProductDetailView,
    ProductListView,
    ExportEnquiryCreateView,
    CropSeasonOperationsView,
    FarmOperationsView,
    HarvestOperationsView,
    InventoryMovementOperationsView,
    ProcessingRecordOperationsView,
    ProductionBatchOperationsView,
    health,
)

urlpatterns = [
    path("health/", health, name="health"),
    path("v1/categories/", ProductCategoryListView.as_view(), name="product-category-list"),
    path("v1/enquiries/", ExportEnquiryCreateView.as_view(), name="enquiry-create"),
    path("v1/products/", ProductListView.as_view(), name="product-list"),
    path(
        "v1/operations/farms/",
        FarmOperationsView.as_view(),
        name="operations-farm-list",
    ),
    path(
        "v1/operations/crop-seasons/",
        CropSeasonOperationsView.as_view(),
        name="operations-crop-season-list",
    ),
    path(
        "v1/operations/harvests/",
        HarvestOperationsView.as_view(),
        name="operations-harvest-list",
    ),
    path(
        "v1/operations/batches/",
        ProductionBatchOperationsView.as_view(),
        name="operations-batch-list",
    ),
    path(
        "v1/operations/processing-records/",
        ProcessingRecordOperationsView.as_view(),
        name="operations-processing-record-list",
    ),
    path(
        "v1/operations/inventory-movements/",
        InventoryMovementOperationsView.as_view(),
        name="operations-inventory-movement-list",
    ),
    path(
        "v1/products/<slug:slug>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
]
