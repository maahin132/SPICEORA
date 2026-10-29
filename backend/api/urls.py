from django.urls import path

from .views import (
    ProductCategoryListView,
    ProductDetailView,
    ProductListView,
    health,
)

urlpatterns = [
    path("health/", health, name="health"),
    path("v1/categories/", ProductCategoryListView.as_view(), name="product-category-list"),
    path("v1/products/", ProductListView.as_view(), name="product-list"),
    path(
        "v1/products/<slug:slug>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
]
