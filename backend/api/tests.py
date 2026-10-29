from io import BytesIO

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.urls import reverse
from PIL import Image
from rest_framework.test import APITestCase

from .models import Product, ProductCategory


class HealthEndpointTests(SimpleTestCase):
    def test_health_endpoint_returns_ok(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class PublicCatalogApiTests(APITestCase):
    def setUp(self):
        self.cumin = ProductCategory.objects.get(slug="cumin")
        self.fennel = ProductCategory.objects.get(slug="fennel")
        self.inactive_category = ProductCategory.objects.create(
            name="Inactive category",
            slug="inactive-category",
            is_active=False,
        )
        self.published_product = Product.objects.create(
            category=self.cumin,
            slug="cumin-seeds",
            name="Cumin seeds",
            summary="Approved test summary.",
            description="Approved test description.",
            is_published=True,
        )
        Product.objects.create(
            category=self.fennel,
            slug="unpublished-fennel",
            name="Unpublished fennel",
            summary="Internal test summary.",
            description="Internal test description.",
        )
        Product.objects.create(
            category=self.inactive_category,
            slug="inactive-category-product",
            name="Inactive category product",
            summary="Internal test summary.",
            description="Internal test description.",
            is_published=True,
        )

    def test_list_returns_only_published_products_and_public_fields(self):
        response = self.client.get(reverse("product-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"],
            [
                {
                    "slug": self.published_product.slug,
                    "name": self.published_product.name,
                    "category": {"slug": "cumin", "name": "Cumin"},
                    "summary": "Approved test summary.",
                    "image": None,
                    "image_alt": "",
                }
            ],
        )

    def test_category_list_contains_only_categories_with_published_products(self):
        response = self.client.get(reverse("product-category-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"slug": "cumin", "name": "Cumin"}])

    def test_category_filter_returns_matching_published_products(self):
        response = self.client.get(
            reverse("product-list"),
            {"category": "cumin"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [product["slug"] for product in response.data["results"]],
            ["cumin-seeds"],
        )

    def test_unknown_or_inactive_category_is_a_validation_error(self):
        for category_slug in ("missing", "inactive-category"):
            with self.subTest(category_slug=category_slug):
                response = self.client.get(
                    reverse("product-list"),
                    {"category": category_slug},
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("category", response.data["errors"])

    def test_invalid_query_parameters_are_rejected(self):
        for query in (
            {"page": "not-a-number"},
            {"unexpected": "value"},
            {"category": ""},
        ):
            with self.subTest(query=query):
                response = self.client.get(reverse("product-list"), query)
                self.assertEqual(response.status_code, 400)
                self.assertIn("errors", response.data)

        response = self.client.get(
            f"{reverse('product-list')}?category=cumin&category=fennel"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("category", response.data["errors"])

    def test_detail_returns_published_product_and_description(self):
        response = self.client.get(
            reverse("product-detail", args=("cumin-seeds",))
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["description"], "Approved test description.")
        self.assertNotIn("is_published", response.data)
        self.assertNotIn("created_at", response.data)

    def test_unpublished_inactive_and_missing_products_return_not_found(self):
        for slug in (
            "unpublished-fennel",
            "inactive-category-product",
            "missing-product",
        ):
            with self.subTest(slug=slug):
                response = self.client.get(
                    reverse("product-detail", args=(slug,))
                )
                self.assertEqual(response.status_code, 404)

    def test_product_models_are_registered_for_staff_catalog_management(self):
        self.assertTrue(admin.site.is_registered(Product))
        self.assertTrue(admin.site.is_registered(ProductCategory))

    def test_product_image_requires_alternative_text(self):
        image_buffer = BytesIO()
        Image.new("RGB", (2, 2)).save(image_buffer, format="PNG")
        product = Product(
            category=self.cumin,
            slug="image-alt-test",
            name="Image alt test",
            summary="Test summary.",
            description="Test description.",
            image=SimpleUploadedFile(
                "product.png",
                image_buffer.getvalue(),
                content_type="image/png",
            ),
        )

        with self.assertRaises(ValidationError) as error:
            product.full_clean()

        self.assertIn("image_alt", error.exception.message_dict)
