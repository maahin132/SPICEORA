from io import BytesIO
from datetime import timedelta
from decimal import Decimal
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
from django.utils import timezone
from PIL import Image
from rest_framework.test import APITestCase

from .models import (
    CropSeason,
    ExportEnquiry,
    Farm,
    Harvest,
    InventoryMovement,
    Product,
    ProductCategory,
    ProcessingRecord,
    ProductionBatch,
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


class FarmTraceabilityTests(APITestCase):
    def setUp(self):
        today = timezone.localdate()
        self.farm = Farm.objects.create(
            reference="FARM-TEST-01",
            name="Traceability test farm",
            location="Test-only location",
        )
        self.season = CropSeason.objects.create(
            reference="SEASON-TEST-01",
            farm=self.farm,
            crop_name="Test crop",
            planting_date=today - timedelta(days=100),
            expected_harvest_date=today - timedelta(days=10),
            status=CropSeason.Status.HARVESTED,
        )
        self.harvest = Harvest.objects.create(
            reference="HARVEST-TEST-01",
            crop_season=self.season,
            harvest_date=today - timedelta(days=5),
            quantity=Decimal("1000"),
            quantity_unit="kg",
        )

    def create_batch(self, **overrides):
        fields = {
            "reference": "BATCH-TEST-01",
            "harvest": self.harvest,
            "product_name": "Test crop batch",
            "batch_date": self.harvest.harvest_date,
            "initial_quantity": Decimal("800"),
            "quantity_unit": "kg",
        }
        fields.update(overrides)
        return ProductionBatch.objects.create(**fields)

    def create_movement(self, batch, movement_type, quantity, unit="kg", **overrides):
        fields = {
            "batch": batch,
            "movement_type": movement_type,
            "quantity": Decimal(quantity),
            "quantity_unit": unit,
            "movement_date": timezone.localdate(),
            "reason": "Test-only inventory event",
        }
        fields.update(overrides)
        return InventoryMovement.objects.create(**fields)

    def test_farm_area_requires_matching_positive_value_and_unit(self):
        farm = Farm(
            reference="FARM-AREA-TEST",
            name="Area test farm",
            location="Test-only location",
            area=Decimal("2"),
        )
        with self.assertRaises(ValidationError) as error:
            farm.full_clean()
        self.assertIn("area", error.exception.message_dict)

        farm.area_unit = Farm.AreaUnit.HECTARE
        farm.area = Decimal("0")
        with self.assertRaises(ValidationError) as error:
            farm.full_clean()
        self.assertIn("area", error.exception.message_dict)

    def test_crop_season_rejects_expected_date_before_planting(self):
        season = CropSeason(
            reference="SEASON-DATE-TEST",
            farm=self.farm,
            crop_name="Test crop",
            planting_date=timezone.localdate(),
            expected_harvest_date=timezone.localdate() - timedelta(days=1),
        )

        with self.assertRaises(ValidationError) as error:
            season.full_clean()

        self.assertIn("expected_harvest_date", error.exception.message_dict)

    def test_harvest_rejects_nonpositive_quantity_and_invalid_dates(self):
        harvest = Harvest(
            reference="HARVEST-INVALID-TEST",
            crop_season=self.season,
            harvest_date=self.season.planting_date - timedelta(days=1),
            quantity=Decimal("0"),
            quantity_unit="kg",
        )

        with self.assertRaises(ValidationError) as error:
            harvest.full_clean()

        self.assertIn("quantity", error.exception.message_dict)
        self.assertIn("harvest_date", error.exception.message_dict)

    def test_batch_is_traceable_and_creation_records_initial_receipt(self):
        batch = self.create_batch()

        self.assertEqual(batch.harvest.crop_season.farm, self.farm)
        self.assertEqual(batch.harvest.crop_season, self.season)
        self.assertEqual(batch.inventory_movements.count(), 1)
        receipt = batch.inventory_movements.get()
        self.assertEqual(
            receipt.movement_type,
            InventoryMovement.MovementType.PRODUCTION_RECEIPT,
        )
        self.assertEqual(receipt.quantity, batch.initial_quantity)
        self.assertEqual(receipt.available_quantity_kg, Decimal("800"))

    def test_batch_quantity_cannot_exceed_unallocated_harvest(self):
        self.create_batch()
        with self.assertRaises(ValidationError) as error:
            self.create_batch(
                reference="BATCH-TEST-02",
                initial_quantity=Decimal("201"),
            )
        self.assertIn("initial_quantity", error.exception.message_dict)

    def test_batch_historical_identity_cannot_be_changed(self):
        batch = self.create_batch()
        batch.initial_quantity = Decimal("700")

        with self.assertRaises(ValidationError) as error:
            batch.save()

        self.assertIn("historical", str(error.exception).lower())

    def test_processing_record_requires_valid_batch_dates_and_quantity_pairs(self):
        batch = self.create_batch()
        processing = ProcessingRecord(
            batch=batch,
            activity="Test activity",
            activity_date=batch.batch_date - timedelta(days=1),
            input_quantity=Decimal("2"),
            input_unit="",
        )

        with self.assertRaises(ValidationError) as error:
            processing.full_clean()

        self.assertIn("activity_date", error.exception.message_dict)
        self.assertIn("input_quantity", error.exception.message_dict)

    def test_processing_record_does_not_invent_inventory_events(self):
        batch = self.create_batch()
        processing = ProcessingRecord.objects.create(
            batch=batch,
            activity="Owner-recorded activity",
            activity_date=timezone.localdate(),
            description="Test event only.",
        )

        self.assertEqual(processing.batch, batch)
        self.assertIsNone(processing.input_quantity)
        self.assertEqual(batch.inventory_movements.count(), 1)
        processing.description = "Attempted retrospective edit."
        with self.assertRaises(ValidationError):
            processing.save()
        with self.assertRaises(ValidationError):
            processing.delete()

    def test_inventory_movement_reservation_release_and_dispatch_calculation(self):
        batch = self.create_batch()
        reservation = self.create_movement(
            batch,
            InventoryMovement.MovementType.RESERVATION,
            "0.300",
            unit="metric_tonne",
        )
        self.assertEqual(reservation.available_quantity_kg, Decimal("500"))

        release = self.create_movement(
            batch,
            InventoryMovement.MovementType.RESERVATION_RELEASE,
            "100",
        )
        self.assertEqual(release.available_quantity_kg, Decimal("600"))

        dispatch = self.create_movement(
            batch,
            InventoryMovement.MovementType.DISPATCH,
            "0.500",
            unit="metric_tonne",
        )
        self.assertEqual(dispatch.available_quantity_kg, Decimal("300"))

    def test_inventory_prevents_negative_available_stock_and_invalid_release(self):
        batch = self.create_batch()
        with self.assertRaises(ValidationError) as error:
            self.create_movement(
                batch,
                InventoryMovement.MovementType.RESERVATION,
                "801",
            )
        self.assertIn("quantity", error.exception.message_dict)

        self.create_movement(
            batch,
            InventoryMovement.MovementType.RESERVATION,
            "500",
        )
        with self.assertRaises(ValidationError) as error:
            self.create_movement(
                batch,
                InventoryMovement.MovementType.RESERVATION_RELEASE,
                "501",
            )
        self.assertIn("quantity", error.exception.message_dict)

    def test_inventory_rejects_dispatch_beyond_physical_stock(self):
        batch = self.create_batch()

        with self.assertRaises(ValidationError) as error:
            self.create_movement(
                batch,
                InventoryMovement.MovementType.DISPATCH,
                "801",
            )

        self.assertIn("quantity", error.exception.message_dict)

    def test_inventory_movements_are_immutable_and_backdating_is_rejected(self):
        batch = self.create_batch()
        movement = self.create_movement(
            batch,
            InventoryMovement.MovementType.PROCESSING_INCREASE,
            "10",
        )
        movement.reason = "Edited after the fact"
        with self.assertRaises(ValidationError):
            movement.save()
        with self.assertRaises(ValidationError):
            movement.delete()

        with self.assertRaises(ValidationError) as error:
            self.create_movement(
                batch,
                InventoryMovement.MovementType.PROCESSING_INCREASE,
                "1",
                movement_date=timezone.localdate() - timedelta(days=1),
            )
        self.assertIn("movement_date", error.exception.message_dict)

    def test_protected_foreign_keys_preserve_farm_to_batch_history(self):
        batch = self.create_batch()
        for record in (self.farm, self.season, self.harvest, batch):
            with self.subTest(model=type(record).__name__):
                with self.assertRaises(ProtectedError):
                    record.delete()

    def test_all_traceability_models_are_registered_in_admin(self):
        for model in (
            Farm,
            CropSeason,
            Harvest,
            ProductionBatch,
            ProcessingRecord,
            InventoryMovement,
        ):
            with self.subTest(model=model.__name__):
                self.assertTrue(admin.site.is_registered(model))

    def test_operations_api_requires_staff_and_model_permissions(self):
        url = reverse("operations-farm-list")

        self.assertIn(self.client.get(url).status_code, (401, 403))

        user_model = get_user_model()
        ordinary_user = user_model.objects.create_user(
            username="operations-regular",
            password="test-only-password",
        )
        self.client.force_authenticate(ordinary_user)
        self.assertEqual(self.client.get(url).status_code, 403)

        staff_user = user_model.objects.create_user(
            username="operations-staff",
            password="test-only-password",
            is_staff=True,
        )
        self.client.force_authenticate(staff_user)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_authorized_staff_can_create_and_list_farms(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        staff_user = get_user_model().objects.create_user(
            username="farm-api-staff",
            password="test-only-password",
            is_staff=True,
        )
        content_type = ContentType.objects.get_for_model(Farm)
        staff_user.user_permissions.add(
            Permission.objects.get(content_type=content_type, codename="view_farm"),
            Permission.objects.get(content_type=content_type, codename="add_farm"),
        )
        self.client.force_authenticate(staff_user)
        url = reverse("operations-farm-list")
        payload = {
            "reference": "API-FARM-01",
            "name": "API test farm",
            "location": "Test-only location",
            "area": None,
            "area_unit": "",
            "description": "",
            "internal_notes": "Private test note",
            "is_active": True,
        }

        created = self.client.post(url, payload, format="json")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["reference"], "API-FARM-01")
        self.assertEqual(created.data["internal_notes"], "Private test note")

        listed = self.client.get(url)
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.data["count"], 2)
        self.assertEqual(len(listed.data["results"]), 2)

    def test_staff_api_creates_traceable_season_harvest_batch_and_processing(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        staff_user = get_user_model().objects.create_user(
            username="traceability-api-staff",
            password="test-only-password",
            is_staff=True,
        )
        models = (Farm, CropSeason, Harvest, ProductionBatch, ProcessingRecord)
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            staff_user.user_permissions.add(
                Permission.objects.get(
                    content_type=content_type,
                    codename=f"add_{model._meta.model_name}",
                )
            )
        self.client.force_authenticate(staff_user)
        today = timezone.localdate()
        farm_response = self.client.post(
            reverse("operations-farm-list"),
            {
                "reference": "API-TRACE-FARM",
                "name": "Traceability API test farm",
                "location": "Test-only location",
            },
            format="json",
        )
        self.assertEqual(farm_response.status_code, 201)

        season_response = self.client.post(
            reverse("operations-crop-season-list"),
            {
                "reference": "API-TRACE-SEASON",
                "farm_reference": "API-TRACE-FARM",
                "crop_name": "Test crop",
                "planting_date": (today - timedelta(days=10)).isoformat(),
                "expected_harvest_date": today.isoformat(),
                "status": CropSeason.Status.HARVESTED,
            },
            format="json",
        )
        self.assertEqual(season_response.status_code, 201)

        harvest_response = self.client.post(
            reverse("operations-harvest-list"),
            {
                "reference": "API-TRACE-HARVEST",
                "crop_season_reference": "API-TRACE-SEASON",
                "harvest_date": today.isoformat(),
                "quantity": "200",
                "quantity_unit": "kg",
            },
            format="json",
        )
        self.assertEqual(harvest_response.status_code, 201)

        batch_response = self.client.post(
            reverse("operations-batch-list"),
            {
                "reference": "API-TRACE-BATCH",
                "harvest_reference": "API-TRACE-HARVEST",
                "product_name": "Test crop",
                "batch_date": today.isoformat(),
                "initial_quantity": "150",
                "quantity_unit": "kg",
            },
            format="json",
        )
        self.assertEqual(batch_response.status_code, 201)
        self.assertEqual(
            batch_response.data["farm_reference"],
            "API-TRACE-FARM",
        )
        self.assertEqual(
            batch_response.data["crop_season_reference"],
            "API-TRACE-SEASON",
        )
        self.assertEqual(batch_response.data["available_quantity_kg"], "150.000")

        processing_response = self.client.post(
            reverse("operations-processing-record-list"),
            {
                "batch_reference": "API-TRACE-BATCH",
                "activity": "Recorded test activity",
                "activity_date": today.isoformat(),
                "description": "Test-only processing record.",
            },
            format="json",
        )
        self.assertEqual(processing_response.status_code, 201)
        self.assertEqual(
            processing_response.data["batch_reference"],
            "API-TRACE-BATCH",
        )

    def test_invalid_farm_payload_returns_field_errors(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        staff_user = get_user_model().objects.create_user(
            username="invalid-farm-api-staff",
            password="test-only-password",
            is_staff=True,
        )
        content_type = ContentType.objects.get_for_model(Farm)
        staff_user.user_permissions.add(
            Permission.objects.get(content_type=content_type, codename="add_farm")
        )
        self.client.force_authenticate(staff_user)

        response = self.client.post(
            reverse("operations-farm-list"),
            {
                "reference": "API-FARM-INVALID",
                "name": "Invalid farm",
                "location": "Test-only location",
                "area": "2",
                "area_unit": "",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("area", response.data["errors"])

    def test_operations_collection_is_paginated(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        Farm.objects.bulk_create(
            [
                Farm(
                    reference=f"PAGINATION-{index:02}",
                    name=f"Test farm {index}",
                    location="Test-only location",
                )
                for index in range(26)
            ]
        )
        staff_user = get_user_model().objects.create_user(
            username="pagination-api-staff",
            password="test-only-password",
            is_staff=True,
        )
        content_type = ContentType.objects.get_for_model(Farm)
        staff_user.user_permissions.add(
            Permission.objects.get(content_type=content_type, codename="view_farm")
        )
        self.client.force_authenticate(staff_user)

        first_page = self.client.get(reverse("operations-farm-list"))
        second_page = self.client.get(
            reverse("operations-farm-list"),
            {"page": 2},
        )

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(first_page.data["count"], 27)
        self.assertEqual(len(first_page.data["results"]), 25)
        self.assertEqual(len(second_page.data["results"]), 2)

    def test_correction_movements_require_extra_approval_permission(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        batch = self.create_batch()
        staff_user = get_user_model().objects.create_user(
            username="inventory-api-staff",
            password="test-only-password",
            is_staff=True,
        )
        content_type = ContentType.objects.get_for_model(InventoryMovement)
        staff_user.user_permissions.add(
            Permission.objects.get(
                content_type=content_type,
                codename="add_inventorymovement",
            )
        )
        self.client.force_authenticate(staff_user)
        payload = {
            "batch_reference": batch.reference,
            "movement_type": InventoryMovement.MovementType.CORRECTION_IN,
            "quantity": "10",
            "quantity_unit": "kg",
            "movement_date": timezone.localdate().isoformat(),
            "reason": "Approved test correction",
            "internal_notes": "Staff-only test note.",
        }
        url = reverse("operations-inventory-movement-list")

        denied = self.client.post(url, payload, format="json")
        self.assertEqual(denied.status_code, 403)

        staff_user.user_permissions.add(
            Permission.objects.get(
                content_type=content_type,
                codename="approve_inventory_correction",
            )
        )
        staff_user = get_user_model().objects.get(pk=staff_user.pk)
        self.client.force_authenticate(staff_user)
        approved = self.client.post(url, payload, format="json")
        self.assertEqual(approved.status_code, 201)
        correction = InventoryMovement.objects.get(
            movement_type=InventoryMovement.MovementType.CORRECTION_IN
        )
        self.assertEqual(correction.available_quantity_kg, Decimal("810.000"))

    def test_operations_api_does_not_allow_updates_or_deletes(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        staff_user = get_user_model().objects.create_user(
            username="operations-view-staff",
            password="test-only-password",
            is_staff=True,
        )
        content_type = ContentType.objects.get_for_model(Farm)
        staff_user.user_permissions.add(
            Permission.objects.get(content_type=content_type, codename="change_farm")
        )
        self.client.force_authenticate(staff_user)

        response = self.client.put(
            reverse("operations-farm-list"),
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 405)

    def test_staff_api_uses_session_authentication_and_csrf_for_writes(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from rest_framework.test import APIClient

        staff_user = get_user_model().objects.create_user(
            username="csrf-farm-staff",
            password="test-only-password",
            is_staff=True,
        )
        content_type = ContentType.objects.get_for_model(Farm)
        staff_user.user_permissions.add(
            Permission.objects.get(content_type=content_type, codename="add_farm")
        )
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(staff_user)

        response = client.post(
            reverse("operations-farm-list"),
            {
                "reference": "CSRF-FARM-01",
                "name": "CSRF test farm",
                "location": "Test-only location",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Farm.objects.filter(reference="CSRF-FARM-01").exists())

    def test_admin_lists_operational_records_and_disables_historical_deletion(self):
        batch = self.create_batch()
        admin_user = get_user_model().objects.create_superuser(
            username="operations-admin",
            email="operations-admin@example.com",
            password="test-only-password",
        )
        self.client.force_login(admin_user)

        farm_list = self.client.get(reverse("admin:api_farm_changelist"))
        batch_change = self.client.get(
            reverse("admin:api_productionbatch_change", args=(batch.pk,))
        )
        movement_change = self.client.get(
            reverse(
                "admin:api_inventorymovement_change",
                args=(batch.inventory_movements.get().pk,),
            )
        )

        self.assertEqual(farm_list.status_code, 200)
        self.assertEqual(batch_change.status_code, 200)
        self.assertContains(batch_change, "Inventory")
        self.assertEqual(movement_change.status_code, 200)
        self.assertNotContains(movement_change, 'name="_save"')
        self.assertEqual(
            self.client.get(
                reverse(
                    "admin:api_inventorymovement_delete",
                    args=(batch.inventory_movements.get().pk,),
                )
            ).status_code,
            403,
        )

    def test_admin_batch_creation_records_initial_inventory_receipt(self):
        admin_user = get_user_model().objects.create_superuser(
            username="batch-admin",
            email="batch-admin@example.com",
            password="test-only-password",
        )
        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("admin:api_productionbatch_add"),
            {
                "reference": "ADMIN-BATCH-01",
                "harvest": self.harvest.pk,
                "product_name": "Test crop batch",
                "batch_date": timezone.localdate().isoformat(),
                "initial_quantity": "200",
                "quantity_unit": "kg",
                "status": ProductionBatch.Status.RECORDED,
                "internal_notes": "Test-only admin record.",
                "processing_records-TOTAL_FORMS": "0",
                "processing_records-INITIAL_FORMS": "0",
                "processing_records-MIN_NUM_FORMS": "0",
                "processing_records-MAX_NUM_FORMS": "1000",
                "inventory_movements-TOTAL_FORMS": "0",
                "inventory_movements-INITIAL_FORMS": "0",
                "inventory_movements-MIN_NUM_FORMS": "0",
                "inventory_movements-MAX_NUM_FORMS": "1000",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        batch = ProductionBatch.objects.get(reference="ADMIN-BATCH-01")
        self.assertEqual(batch.inventory_movements.count(), 1)
        self.assertEqual(
            batch.inventory_movements.get().movement_type,
            InventoryMovement.MovementType.PRODUCTION_RECEIPT,
        )
