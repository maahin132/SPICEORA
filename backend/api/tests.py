from io import BytesIO
from pathlib import Path
import tempfile

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.deletion import ProtectedError
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework.test import APITestCase

from .models import (
    ExportEnquiry,
    Product,
    ProductCategory,
    product_image_upload_to,
)


def uploaded_image(name="product.png", size=(2, 2), image_format="PNG"):
    image_buffer = BytesIO()
    Image.new("RGB", size, color=(32, 59, 48)).save(
        image_buffer,
        format=image_format,
    )
    return SimpleUploadedFile(
        name,
        image_buffer.getvalue(),
        content_type=f"image/{image_format.lower()}",
    )


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

    def test_category_list_contains_active_categories_for_enquiry_choices(self):
        response = self.client.get(reverse("product-category-list"))

        self.assertEqual(response.status_code, 200)
        self.assertIn({"slug": "cumin", "name": "Cumin"}, response.data)
        self.assertIn({"slug": "fennel", "name": "Fennel"}, response.data)
        self.assertNotIn(
            {"slug": "inactive-category", "name": "Inactive category"},
            response.data,
        )

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
        product = Product(
            category=self.cumin,
            slug="image-alt-test",
            name="Image alt test",
            summary="Test summary.",
            description="Test description.",
            image=uploaded_image(),
        )

        with self.assertRaises(ValidationError) as error:
            product.full_clean()

        self.assertIn("image_alt", error.exception.message_dict)

    def test_product_image_rejects_mismatched_format(self):
        product = Product(
            category=self.cumin,
            slug="image-format-test",
            name="Image format test",
            summary="Test summary.",
            description="Test description.",
            image=uploaded_image(name="product.jpg"),
            image_alt="A test product image.",
        )

        with self.assertRaises(ValidationError) as error:
            product.full_clean()

        self.assertIn("image", error.exception.message_dict)

    def test_product_image_rejects_executable_extension_and_non_image_content(self):
        for name, content in (
            ("payload.exe", uploaded_image().read()),
            ("payload.png", b"MZ this is not an image"),
        ):
            with self.subTest(name=name):
                product = Product(
                    category=self.cumin,
                    slug=f"unsafe-image-{name.split('.')[-1]}",
                    name="Unsafe image test",
                    summary="Test summary.",
                    description="Test description.",
                    image=SimpleUploadedFile(name, content),
                    image_alt="A test product image.",
                )
                with self.assertRaises(ValidationError) as error:
                    product.full_clean()
                self.assertIn("image", error.exception.message_dict)

    def test_product_image_accepts_supported_matching_formats(self):
        for extension, image_format in (
            ("jpg", "JPEG"),
            ("jpeg", "JPEG"),
            ("png", "PNG"),
            ("webp", "WEBP"),
        ):
            with self.subTest(extension=extension):
                product = Product(
                    category=self.cumin,
                    slug=f"image-format-{extension}",
                    name="Image format test",
                    summary="Test summary.",
                    description="Test description.",
                    image=uploaded_image(
                        name=f"product.{extension}",
                        image_format=image_format,
                    ),
                    image_alt="A test product image.",
                )
                product.full_clean()

    def test_product_image_rejects_oversized_file(self):
        product = Product(
            category=self.cumin,
            slug="image-size-test",
            name="Image size test",
            summary="Test summary.",
            description="Test description.",
            image=SimpleUploadedFile(
                "large.png",
                b"x" * (5 * 1024 * 1024 + 1),
                content_type="image/png",
            ),
            image_alt="A test product image.",
        )

        with self.assertRaises(ValidationError) as error:
            product.full_clean()

        self.assertIn("5 MB or smaller", str(error.exception))

    def test_product_image_rejects_oversized_dimensions(self):
        product = Product(
            category=self.cumin,
            slug="image-dimensions-test",
            name="Image dimensions test",
            summary="Test summary.",
            description="Test description.",
            image=uploaded_image(size=(8001, 1)),
            image_alt="A test product image.",
        )

        with self.assertRaises(ValidationError) as error:
            product.full_clean()

        self.assertIn("40 megapixels", str(error.exception))

    def test_product_image_upload_uses_random_safe_filename_and_public_url(self):
        product = Product(
            category=self.cumin,
            slug="image-upload-test",
            name="Image upload test",
            summary="Test summary.",
            description="Test description.",
            image=uploaded_image(name=r"..\unsafe\product PHOTO.PNG"),
            image_alt="A test product image.",
            is_published=True,
        )
        self.assertRegex(
            product_image_upload_to(product, r"..\unsafe\product PHOTO.PNG"),
            r"^products/[0-9a-f]{32}\.png$",
        )

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                product.full_clean()
                product.save()
                self.assertRegex(
                    product.image.name,
                    r"^products/[0-9a-f]{32}\.png$",
                )
                self.assertTrue(Path(media_root, product.image.name).is_file())

                response = self.client.get(
                    reverse("product-detail", args=(product.slug,))
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["image"],
            f"http://testserver/media/{product.image.name}",
        )
        self.assertEqual(response.data["image_alt"], "A test product image.")


class ProductAdminWorkflowTests(APITestCase):
    def setUp(self):
        self.category = ProductCategory.objects.get(slug="cumin")
        self.admin_user = get_user_model().objects.create_superuser(
            username="product-admin",
            email="product-admin@example.com",
            password="test-only-password",
        )
        self.client.force_login(self.admin_user)

    def product_form_data(self, **overrides):
        data = {
            "name": "Admin managed cumin",
            "slug": "admin-managed-cumin",
            "category": str(self.category.pk),
            "summary": "Owner-approved short description.",
            "description": "Owner-approved full description.",
            "image_alt": "",
            "is_published": "",
            "sort_order": "0",
            "_save": "Save",
        }
        data.update(overrides)
        return data

    def test_admin_can_create_product_as_unpublished_draft(self):
        response = self.client.post(
            reverse("admin:api_product_add"),
            self.product_form_data(),
        )

        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(slug="admin-managed-cumin")
        self.assertFalse(product.is_published)
        self.assertEqual(product.category, self.category)

    def test_admin_can_update_product_content_and_publication_state(self):
        product = Product.objects.create(
            category=self.category,
            slug="admin-managed-cumin",
            name="Admin managed cumin",
            summary="Old summary.",
            description="Old description.",
        )
        change_url = reverse("admin:api_product_change", args=(product.pk,))

        response = self.client.post(
            change_url,
            self.product_form_data(
                summary="Updated summary.",
                description="Updated description.",
                is_published="on",
            ),
        )

        self.assertEqual(response.status_code, 302)
        product.refresh_from_db()
        self.assertEqual(product.summary, "Updated summary.")
        self.assertTrue(product.is_published)

        self.client.post(change_url, self.product_form_data())
        product.refresh_from_db()
        self.assertFalse(product.is_published)
        self.assertEqual(
            self.client.get(
                reverse("product-detail", args=(product.slug,))
            ).status_code,
            404,
        )

    def test_admin_product_list_exposes_search_filters_order_and_image_preview(self):
        from .admin import ProductAdmin

        product = Product.objects.create(
            category=self.category,
            slug="admin-managed-cumin",
            name="Admin managed cumin",
            summary="Test summary.",
            description="Test description.",
        )
        model_admin = ProductAdmin(Product, admin.site)

        self.assertEqual(model_admin.search_fields, ("name", "slug"))
        self.assertEqual(model_admin.list_filter, ("is_published", "category"))
        self.assertIn("sort_order", model_admin.ordering)
        self.assertIn("created_at", model_admin.list_display)
        self.assertEqual(model_admin.image_preview(product), "No image uploaded.")

        product.image.name = "products/missing-image.png"
        self.assertEqual(model_admin.image_preview(product), "Image file is missing.")

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                product.image.save("test-image.png", uploaded_image(), save=False)
                preview = str(model_admin.image_preview(product))
        self.assertIn("<img", preview)
        self.assertIn(product.image.name, preview)

    def test_admin_delete_confirmation_and_delete_of_unlinked_product(self):
        product = Product.objects.create(
            category=self.category,
            slug="deletable-product",
            name="Deletable product",
            summary="Test summary.",
            description="Test description.",
        )
        delete_url = reverse("admin:api_product_delete", args=(product.pk,))

        confirmation = self.client.get(delete_url)
        self.assertEqual(confirmation.status_code, 200)
        self.assertContains(confirmation, "Are you sure")

        response = self.client.post(delete_url, {"post": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())
        self.assertTrue(ProductCategory.objects.filter(pk=self.category.pk).exists())

    def test_product_and_category_deletion_preserve_enquiry_relationships(self):
        product = Product.objects.create(
            category=self.category,
            slug="enquiry-linked-product",
            name="Enquiry linked product",
            summary="Test summary.",
            description="Test description.",
        )
        enquiry = ExportEnquiry.objects.create(
            full_name="Test buyer",
            email="test-buyer@example.com",
            country="Test country",
            category=self.category,
            product=product,
            product_name_snapshot=product.name,
        )

        with self.assertRaises(ProtectedError):
            product.delete()
        with self.assertRaises(ProtectedError):
            self.category.delete()

        product.refresh_from_db()
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.product_id, product.pk)
        self.assertEqual(enquiry.category_id, self.category.pk)
        self.assertTrue(ProductCategory.objects.filter(pk=self.category.pk).exists())


class ExportEnquiryApiTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.cumin = ProductCategory.objects.get(slug="cumin")
        ProductCategory.objects.create(
            name="Inactive category",
            slug="inactive-category",
            is_active=False,
        )
        self.product = Product.objects.create(
            category=self.cumin,
            slug="approved-cumin",
            name="Approved cumin",
            summary="Approved summary.",
            description="Approved description.",
            is_published=True,
        )
        Product.objects.create(
            category=ProductCategory.objects.get(slug="fennel"),
            slug="unpublished-fennel",
            name="Unpublished fennel",
            summary="Internal summary.",
            description="Internal description.",
        )
        self.payload = {
            "full_name": "A Buyer",
            "company_name": "Buyer Company",
            "email": "buyer@example.com",
            "phone": "+1 555 0100",
            "country": "Example Country",
            "category_slug": "cumin",
            "quantity": "12.5",
            "quantity_unit": "kg",
            "message": "Please contact me about this category.",
        }

    def submit(self, payload=None):
        return self.client.post(
            reverse("enquiry-create"),
            payload if payload is not None else self.payload,
            format="json",
        )

    def test_valid_category_enquiry_is_persisted_and_returns_reference(self):
        response = self.submit()

        self.assertEqual(response.status_code, 201)
        self.assertIn("reference", response.data)
        self.assertEqual(ExportEnquiry.objects.count(), 1)
        enquiry = ExportEnquiry.objects.get()
        self.assertEqual(enquiry.full_name, "A Buyer")
        self.assertEqual(enquiry.category, self.cumin)
        self.assertIsNone(enquiry.product)
        self.assertEqual(enquiry.quantity, 12.5)
        self.assertEqual(enquiry.status, ExportEnquiry.Status.NEW)

    def test_product_enquiry_records_category_and_product_snapshot(self):
        payload = {key: value for key, value in self.payload.items() if key != "category_slug"}
        payload["product_slug"] = self.product.slug

        response = self.submit(payload)

        self.assertEqual(response.status_code, 201)
        enquiry = ExportEnquiry.objects.get()
        self.assertEqual(enquiry.product, self.product)
        self.assertEqual(enquiry.category, self.cumin)
        self.assertEqual(enquiry.product_name_snapshot, "Approved cumin")

    def test_missing_required_fields_are_rejected(self):
        for field in (
            "full_name",
            "email",
            "country",
            "category_slug",
            "quantity",
            "quantity_unit",
        ):
            with self.subTest(field=field):
                cache.clear()
                payload = self.payload.copy()
                payload.pop(field)
                response = self.submit(payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data["errors"])
        self.assertEqual(ExportEnquiry.objects.count(), 0)

    def test_invalid_email_is_rejected(self):
        payload = self.payload.copy()
        payload["email"] = "not-an-email"

        response = self.submit(payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data["errors"])

    def test_invalid_or_incomplete_quantity_is_rejected(self):
        for quantity in ("0", "-2", "1.1234", "not-a-number"):
            with self.subTest(quantity=quantity):
                payload = self.payload.copy()
                payload["quantity"] = quantity
                response = self.submit(payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn("quantity", response.data["errors"])

        payload = self.payload.copy()
        payload["quantity_unit"] = ""
        response = self.submit(payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("quantity_unit", response.data["errors"])

    def test_unknown_inactive_or_unpublished_interest_is_rejected(self):
        for field, value in (
            ("category_slug", "missing"),
            ("category_slug", "inactive-category"),
            ("product_slug", "unpublished-fennel"),
            ("product_slug", "missing"),
        ):
            with self.subTest(field=field, value=value):
                payload = {
                    key: item
                    for key, item in self.payload.items()
                    if key not in {"category_slug", "product_slug"}
                }
                payload[field] = value
                response = self.submit(payload)
                self.assertEqual(response.status_code, 400)

    def test_exactly_one_product_or_category_must_be_selected(self):
        response = self.submit(
            {
                **self.payload,
                "product_slug": self.product.slug,
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("category_slug", response.data["errors"])

    def test_model_rejects_inconsistent_quantity_or_product_category(self):
        enquiry = ExportEnquiry(
            full_name="A Buyer",
            email="buyer@example.com",
            country="Example Country",
            category=self.cumin,
            product=self.product,
            quantity=12,
            quantity_unit="",
        )
        with self.assertRaises(ValidationError):
            enquiry.full_clean()

        enquiry.quantity_unit = "kg"
        enquiry.category = ProductCategory.objects.get(slug="fennel")
        with self.assertRaises(ValidationError) as error:
            enquiry.full_clean()
        self.assertIn("product", error.exception.message_dict)

    def test_public_response_does_not_expose_internal_fields(self):
        response = self.submit()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.data), {"reference", "message"})
        self.assertNotIn("internal_notes", response.data)
        self.assertNotIn("status", response.data)

    def test_public_api_has_no_enquiry_read_operation(self):
        response = self.client.get(reverse("enquiry-create"))

        self.assertEqual(response.status_code, 405)

    @override_settings(
        REST_FRAMEWORK={"DEFAULT_THROTTLE_RATES": {"public_enquiry": "1/hour"}}
    )
    def test_rate_limit_returns_429_after_one_submission(self):
        cache.clear()
        self.addCleanup(cache.clear)

        first = self.submit()
        second = self.submit()

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 429)
        self.assertEqual(ExportEnquiry.objects.count(), 1)


class ExportEnquiryAdminTests(APITestCase):
    def setUp(self):
        self.category = ProductCategory.objects.get(slug="cumin")
        self.enquiry = ExportEnquiry.objects.create(
            full_name="A Buyer",
            email="buyer@example.com",
            country="Example Country",
            category=self.category,
        )
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            username="catalog-admin",
            email="admin@example.com",
            password="test-only-password",
        )
        self.client.force_login(self.admin_user)

    def test_staff_can_update_status_and_internal_notes(self):
        response = self.client.post(
            reverse("admin:api_exportenquiry_change", args=(self.enquiry.pk,)),
            {
                "full_name": self.enquiry.full_name,
                "company_name": "",
                "email": self.enquiry.email,
                "phone": "",
                "country": self.enquiry.country,
                "category": self.category.pk,
                "product": "",
                "product_name_snapshot": "",
                "quantity": "",
                "quantity_unit": "",
                "message": "",
                "status": ExportEnquiry.Status.IN_PROGRESS,
                "internal_notes": "Staff follow-up note.",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, ExportEnquiry.Status.IN_PROGRESS)
        self.assertEqual(self.enquiry.internal_notes, "Staff follow-up note.")

    def test_staff_cannot_create_enquiries_from_admin(self):
        response = self.client.get(reverse("admin:api_exportenquiry_add"))

        self.assertEqual(response.status_code, 403)
