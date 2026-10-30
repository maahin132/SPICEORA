from decimal import Decimal
import warnings
import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from PIL import Image, UnidentifiedImageError


PRODUCT_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
PRODUCT_IMAGE_MAX_SIZE = 5 * 1024 * 1024
PRODUCT_IMAGE_MAX_DIMENSION = 8000
PRODUCT_IMAGE_MAX_PIXELS = 40_000_000


def product_image_upload_to(instance, filename):
    extension = Path(filename).suffix.lower()
    if extension.lstrip(".") not in PRODUCT_IMAGE_EXTENSIONS:
        raise ValidationError("Upload a JPG, PNG, or WebP product image.")
    return f"products/{uuid.uuid4().hex}{extension}"


def validate_image_size(image):
    if image.size > PRODUCT_IMAGE_MAX_SIZE:
        raise ValidationError("Product images must be 5 MB or smaller.")


def validate_product_image(image):
    extension = Path(image.name).suffix.lower().lstrip(".")
    try:
        image.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(image) as uploaded_image:
                width, height = uploaded_image.size
                expected_format = {
                    "jpg": "JPEG",
                    "jpeg": "JPEG",
                    "png": "PNG",
                    "webp": "WEBP",
                }.get(extension)
                if expected_format is None or uploaded_image.format != expected_format:
                    raise ValidationError(
                        "The image content must match its JPG, PNG, or WebP extension."
                    )
                if (
                    width > PRODUCT_IMAGE_MAX_DIMENSION
                    or height > PRODUCT_IMAGE_MAX_DIMENSION
                    or width * height > PRODUCT_IMAGE_MAX_PIXELS
                ):
                    raise ValidationError(
                        "Product images must be no larger than 8000 px per side "
                        "or 40 megapixels."
                    )
    except ValidationError:
        raise
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        UnidentifiedImageError,
    ) as error:
        raise ValidationError("Upload a valid JPG, PNG, or WebP image.") from error
    finally:
        image.seek(0)


class ProductCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name_plural = "product categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="products",
    )
    slug = models.SlugField(max_length=150, unique=True)
    name = models.CharField(max_length=120)
    summary = models.CharField(max_length=280)
    description = models.TextField()
    image = models.ImageField(
        upload_to=product_image_upload_to,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=PRODUCT_IMAGE_EXTENSIONS),
            validate_image_size,
            validate_product_image,
        ],
    )
    image_alt = models.CharField(max_length=180, blank=True)
    is_published = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "name")

    def clean(self):
        super().clean()
        if self.image and not self.image_alt.strip():
            raise ValidationError(
                {"image_alt": "Add descriptive alternative text for the image."}
            )

    def __str__(self):
        return self.name


class ExportEnquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In progress"
        RESPONDED = "responded", "Responded"
        CLOSED = "closed", "Closed"

    class QuantityUnit(models.TextChoices):
        KILOGRAM = "kg", "Kilograms"
        METRIC_TONNE = "metric_tonne", "Metric tonnes"

    public_reference = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    full_name = models.CharField(max_length=120)
    company_name = models.CharField(max_length=160, blank=True)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=40, blank=True)
    country = models.CharField(max_length=100)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="enquiries",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="enquiries",
        null=True,
        blank=True,
    )
    product_name_snapshot = models.CharField(max_length=120, blank=True)
    quantity = models.DecimalField(
        max_digits=16,
        decimal_places=3,
        null=True,
        blank=True,
    )
    quantity_unit = models.CharField(
        max_length=20,
        choices=QuantityUnit.choices,
        blank=True,
    )
    message = models.TextField(blank=True, max_length=5000)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(quantity__isnull=True, quantity_unit="")
                    | (
                        Q(quantity__gt=0)
                        & Q(quantity_unit__in=("kg", "metric_tonne"))
                    )
                ),
                name="enquiry_quantity_unit_consistent",
            ),
        ]

    def clean(self):
        super().clean()
        if (self.quantity is None) != (not self.quantity_unit):
            raise ValidationError(
                {
                    "quantity": (
                        "Provide both an estimated quantity and its unit, "
                        "or leave both blank."
                    )
                }
            )
        if self.quantity is not None and self.quantity <= 0:
            raise ValidationError(
                {"quantity": "Enter a quantity greater than zero."}
            )
        if self.product_id and self.category_id:
            if self.product.category_id != self.category_id:
                raise ValidationError(
                    {"product": "The selected product must belong to this category."}
                )

    def __str__(self):
        return f"{self.full_name} — {self.country} ({self.public_reference})"


class TraceabilityUnit(models.TextChoices):
    KILOGRAM = "kg", "Kilograms"
    METRIC_TONNE = "metric_tonne", "Metric tonnes"


class Farm(models.Model):
    class AreaUnit(models.TextChoices):
        ACRE = "acre", "Acres"
        HECTARE = "hectare", "Hectares"

    reference = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=160)
    location = models.TextField()
    area = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
    )
    area_unit = models.CharField(
        max_length=12,
        choices=AreaUnit.choices,
        blank=True,
    )
    description = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("reference",)
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(area__isnull=True, area_unit="")
                    | (Q(area__gt=0) & Q(area_unit__in=("acre", "hectare")))
                ),
                name="farm_area_unit_consistent",
            ),
        ]

    def clean(self):
        super().clean()
        if (self.area is None) != (not self.area_unit):
            raise ValidationError(
                {"area": "Provide both area and unit, or leave both blank."}
            )
        if self.area is not None and self.area <= 0:
            raise ValidationError({"area": "Area must be greater than zero."})
        if self.pk:
            original = Farm.objects.filter(pk=self.pk).first()
            if original and original.crop_seasons.exists() and any(
                getattr(original, field) != getattr(self, field)
                for field in ("reference", "name", "location", "area", "area_unit")
            ):
                raise ValidationError(
                    "Farm identity and recorded location/area cannot be changed "
                    "after crop seasons are recorded."
                )

    def __str__(self):
        return f"{self.reference} — {self.name}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class CropSeason(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        GROWING = "growing", "Growing"
        HARVESTED = "harvested", "Harvested"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=40, unique=True)
    farm = models.ForeignKey(
        Farm,
        on_delete=models.PROTECT,
        related_name="crop_seasons",
    )
    crop_name = models.CharField(max_length=120)
    planting_date = models.DateField(null=True, blank=True)
    expected_harvest_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(planting_date__isnull=True)
                    | Q(expected_harvest_date__isnull=True)
                    | Q(expected_harvest_date__gte=models.F("planting_date"))
                ),
                name="season_expected_date_after_planting",
            ),
        ]

    def clean(self):
        super().clean()
        if (
            self.planting_date
            and self.expected_harvest_date
            and self.expected_harvest_date < self.planting_date
        ):
            raise ValidationError(
                {
                    "expected_harvest_date": (
                        "Expected harvest date cannot be before planting date."
                    )
                }
            )
        if self.pk:
            original = CropSeason.objects.filter(pk=self.pk).first()
            if original and original.harvests.exists() and any(
                getattr(original, field) != getattr(self, field)
                for field in ("reference", "farm_id", "crop_name", "planting_date")
            ):
                raise ValidationError(
                    "Season identity, farm, crop, and planting date cannot be "
                    "changed after a harvest is recorded."
                )

    def __str__(self):
        return f"{self.reference} — {self.crop_name} ({self.farm.reference})"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Harvest(models.Model):
    reference = models.CharField(max_length=40, unique=True)
    crop_season = models.ForeignKey(
        CropSeason,
        on_delete=models.PROTECT,
        related_name="harvests",
    )
    harvest_date = models.DateField()
    quantity = models.DecimalField(max_digits=16, decimal_places=3)
    quantity_unit = models.CharField(max_length=20, choices=TraceabilityUnit.choices)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-harvest_date", "-created_at")
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="harvest_quantity_positive",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}
        if self.quantity is not None and self.quantity <= 0:
            errors["quantity"] = "Harvest quantity must be positive."
        if self.crop_season_id and self.harvest_date:
            if (
                self.crop_season.planting_date
                and self.harvest_date < self.crop_season.planting_date
            ):
                errors["harvest_date"] = "Harvest date cannot precede planting date."
            elif self.harvest_date > timezone.localdate():
                errors["harvest_date"] = "A recorded harvest date cannot be in the future."
        if self.pk:
            original = Harvest.objects.filter(pk=self.pk).first()
            if original and original.batches.exists() and any(
                getattr(original, field) != getattr(self, field)
                for field in (
                    "reference",
                    "crop_season_id",
                    "harvest_date",
                    "quantity",
                    "quantity_unit",
                )
            ):
                errors["__all__"] = (
                    "Harvest origin, date, and quantity cannot change after a "
                    "production batch is recorded."
                )
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.reference} — {self.crop_season.crop_name}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ProductionBatch(models.Model):
    class Status(models.TextChoices):
        RECORDED = "recorded", "Recorded"
        PROCESSING = "processing", "Processing"
        STORED = "stored", "Stored"
        ON_HOLD = "on_hold", "On hold"
        CLOSED = "closed", "Closed"

    reference = models.CharField(max_length=40, unique=True)
    harvest = models.ForeignKey(
        Harvest,
        on_delete=models.PROTECT,
        related_name="batches",
    )
    product_name = models.CharField(max_length=160)
    batch_date = models.DateField()
    initial_quantity = models.DecimalField(max_digits=16, decimal_places=3)
    quantity_unit = models.CharField(max_length=20, choices=TraceabilityUnit.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECORDED,
    )
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-batch_date", "-created_at")
        constraints = [
            models.CheckConstraint(
                condition=Q(initial_quantity__gt=0),
                name="batch_initial_quantity_positive",
            ),
        ]

    def clean(self):
        super().clean()
        if self.initial_quantity is not None and self.initial_quantity <= 0:
            raise ValidationError(
                {"initial_quantity": "Initial batch quantity must be positive."}
            )
        if self.harvest_id:
            harvest = self.harvest
            if self.batch_date and self.batch_date < harvest.harvest_date:
                raise ValidationError(
                    {"batch_date": "Batch date cannot precede its harvest date."}
                )
            if self.batch_date and self.batch_date > timezone.localdate():
                raise ValidationError(
                    {"batch_date": "Batch date cannot be in the future."}
                )
            if self.initial_quantity and self.quantity_unit:
                existing = ProductionBatch.objects.filter(harvest_id=self.harvest_id)
                if self.pk:
                    existing = existing.exclude(pk=self.pk)
                already_allocated_kg = sum(
                    (
                        quantity_to_kg(batch.initial_quantity, batch.quantity_unit)
                        for batch in existing.only("initial_quantity", "quantity_unit")
                    ),
                    Decimal("0"),
                )
                requested_kg = quantity_to_kg(
                    self.initial_quantity,
                    self.quantity_unit,
                )
                harvest_kg = quantity_to_kg(
                    harvest.quantity,
                    harvest.quantity_unit,
                )
                if already_allocated_kg + requested_kg > harvest_kg:
                    raise ValidationError(
                        {
                            "initial_quantity": (
                                "Batch quantity exceeds the remaining quantity "
                                "from this harvest."
                            )
                        }
                    )
            if self.pk:
                original = ProductionBatch.objects.filter(pk=self.pk).first()
                if original and any(
                    getattr(original, field) != getattr(self, field)
                    for field in (
                        "reference",
                        "harvest_id",
                        "product_name",
                        "batch_date",
                        "initial_quantity",
                        "quantity_unit",
                    )
                ):
                    raise ValidationError(
                        "Batch identity, origin, date, and initial quantity are "
                        "historical and cannot be changed."
                    )

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.full_clean()
            return super().save(*args, **kwargs)

        with transaction.atomic():
            Harvest.objects.select_for_update().get(pk=self.harvest_id)
            self.full_clean()
            super().save(*args, **kwargs)
            InventoryMovement.objects.create(
                batch=self,
                movement_type=InventoryMovement.MovementType.PRODUCTION_RECEIPT,
                quantity=self.initial_quantity,
                quantity_unit=self.quantity_unit,
                movement_date=self.batch_date,
                reason="Initial production batch receipt",
            )

    def __str__(self):
        return f"{self.reference} — {self.product_name}"


class ProcessingRecord(models.Model):
    batch = models.ForeignKey(
        ProductionBatch,
        on_delete=models.PROTECT,
        related_name="processing_records",
    )
    activity = models.CharField(max_length=120)
    activity_date = models.DateField()
    input_quantity = models.DecimalField(
        max_digits=16,
        decimal_places=3,
        null=True,
        blank=True,
    )
    input_unit = models.CharField(
        max_length=20,
        choices=TraceabilityUnit.choices,
        blank=True,
    )
    output_quantity = models.DecimalField(
        max_digits=16,
        decimal_places=3,
        null=True,
        blank=True,
    )
    output_unit = models.CharField(
        max_length=20,
        choices=TraceabilityUnit.choices,
        blank=True,
    )
    description = models.TextField(blank=True)
    supporting_document_references = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-activity_date", "-created_at")
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(input_quantity__isnull=True, input_unit="")
                    | (Q(input_quantity__gt=0) & Q(input_unit__in=("kg", "metric_tonne")))
                ),
                name="processing_input_pair_positive",
            ),
            models.CheckConstraint(
                condition=(
                    Q(output_quantity__isnull=True, output_unit="")
                    | (
                        Q(output_quantity__gt=0)
                        & Q(output_unit__in=("kg", "metric_tonne"))
                    )
                ),
                name="processing_output_pair_positive",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}
        if (self.input_quantity is None) != (not self.input_unit):
            errors["input_quantity"] = "Provide both input quantity and unit, or neither."
        if (self.output_quantity is None) != (not self.output_unit):
            errors["output_quantity"] = "Provide both output quantity and unit, or neither."
        if self.input_quantity is not None and self.input_quantity <= 0:
            errors["input_quantity"] = "Input quantity must be positive."
        if self.output_quantity is not None and self.output_quantity <= 0:
            errors["output_quantity"] = "Output quantity must be positive."
        if self.batch_id and self.activity_date:
            if self.activity_date < self.batch.batch_date:
                errors["activity_date"] = "Activity date cannot precede batch creation."
            elif self.activity_date > timezone.localdate():
                errors["activity_date"] = "An actual activity date cannot be in the future."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError(
                "Processing records are immutable; record a new event instead."
            )
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "Processing records are historical events and cannot be deleted."
        )

    def __str__(self):
        return f"{self.batch.reference} — {self.activity} ({self.activity_date})"


def inventory_movement_reference():
    return f"INV-{uuid.uuid4().hex.upper()}"


class InventoryMovement(models.Model):
    class MovementType(models.TextChoices):
        PRODUCTION_RECEIPT = "production_receipt", "Production receipt"
        PROCESSING_INCREASE = "processing_increase", "Processing adjustment (increase)"
        PROCESSING_DECREASE = "processing_decrease", "Processing adjustment (decrease)"
        RESERVATION = "reservation", "Reservation"
        RESERVATION_RELEASE = "reservation_release", "Reservation release"
        DISPATCH = "dispatch", "Dispatch"
        CORRECTION_IN = "correction_in", "Approved correction (increase)"
        CORRECTION_OUT = "correction_out", "Approved correction (decrease)"

    reference = models.CharField(
        max_length=48,
        unique=True,
        default=inventory_movement_reference,
    )
    batch = models.ForeignKey(
        ProductionBatch,
        on_delete=models.PROTECT,
        related_name="inventory_movements",
    )
    movement_type = models.CharField(max_length=32, choices=MovementType.choices)
    quantity = models.DecimalField(max_digits=16, decimal_places=3)
    quantity_unit = models.CharField(max_length=20, choices=TraceabilityUnit.choices)
    movement_date = models.DateField()
    reason = models.CharField(max_length=250)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("movement_date", "created_at", "pk")
        permissions = [
            (
                "approve_inventory_correction",
                "Can record approved inventory corrections",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="inventory_movement_quantity_positive",
            ),
        ]

    def clean(self):
        super().clean()
        if self.quantity is not None and self.quantity <= 0:
            raise ValidationError({"quantity": "Movement quantity must be positive."})
        if not self.reason.strip():
            raise ValidationError({"reason": "Enter a reason for this movement."})
        if not self.batch_id:
            return
        if self.movement_date < self.batch.batch_date:
            raise ValidationError(
                {"movement_date": "Movement date cannot precede batch creation."}
            )
        if self.movement_date > timezone.localdate():
            raise ValidationError(
                {"movement_date": "A recorded movement date cannot be in the future."}
            )
        previous = list(
            InventoryMovement.objects.filter(batch_id=self.batch_id)
            .exclude(pk=self.pk)
            .order_by("movement_date", "created_at", "pk")
        )
        if previous and self.movement_date < previous[-1].movement_date:
            raise ValidationError(
                {
                    "movement_date": (
                        "Movement history is append-only; use today's date or a "
                        "date no earlier than the latest movement."
                    )
                }
            )
        if self.movement_type == self.MovementType.PRODUCTION_RECEIPT:
            if previous:
                raise ValidationError(
                    {"movement_type": "The initial production receipt already exists."}
                )
            if (
                self.quantity != self.batch.initial_quantity
                or self.quantity_unit != self.batch.quantity_unit
                or self.movement_date != self.batch.batch_date
            ):
                raise ValidationError(
                    {
                        "quantity": (
                            "The initial receipt must match the batch's initial "
                            "quantity, unit, and date."
                        )
                    }
                )

        on_hand_kg, reserved_kg = inventory_balances(self.batch, previous)
        quantity_kg = quantity_to_kg(self.quantity, self.quantity_unit)
        if self.movement_type == self.MovementType.RESERVATION:
            if quantity_kg > on_hand_kg - reserved_kg:
                raise ValidationError(
                    {"quantity": "Reservation exceeds currently available stock."}
                )
        elif self.movement_type == self.MovementType.RESERVATION_RELEASE:
            if quantity_kg > reserved_kg:
                raise ValidationError(
                    {"quantity": "Reservation release exceeds reserved stock."}
                )
        elif self.movement_type == self.MovementType.DISPATCH:
            if quantity_kg > on_hand_kg:
                raise ValidationError(
                    {"quantity": "Dispatch exceeds physical on-hand stock."}
                )
        elif self.movement_type in {
            self.MovementType.PROCESSING_DECREASE,
            self.MovementType.CORRECTION_OUT,
        }:
            if quantity_kg > on_hand_kg - reserved_kg:
                raise ValidationError(
                    {"quantity": "Movement would reduce available stock below zero."}
                )

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError(
                "Inventory movements are immutable; record a new movement instead."
            )
        with transaction.atomic():
            ProductionBatch.objects.select_for_update().get(pk=self.batch_id)
            self.full_clean()
            return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "Inventory movements are historical records and cannot be deleted."
        )

    @property
    def available_quantity_kg(self):
        on_hand_kg, reserved_kg = inventory_balances(self.batch)
        return on_hand_kg - reserved_kg

    def __str__(self):
        return f"{self.reference} — {self.get_movement_type_display()}"


class AccountProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_profile",
    )
    full_name = models.CharField(max_length=160)
    email_key = models.EmailField(max_length=254, unique=True)
    mobile_number = models.CharField(max_length=16, unique=True)
    email_verified = models.BooleanField(default=False)
    mobile_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email_key


class OTPChallenge(models.Model):
    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"

    class Purpose(models.TextChoices):
        REGISTRATION = "registration", "Registration"
        PASSWORD_RESET = "password_reset", "Password reset"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otp_challenges",
    )
    channel = models.CharField(max_length=8, choices=Channel.choices)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    verified_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=("user", "purpose", "channel", "-created_at"),
                name="otp_account_scope_idx",
            ),
        ]

    def __str__(self):
        return f"{self.user_id} — {self.purpose} — {self.channel}"


def quantity_to_kg(quantity, unit):
    if unit == TraceabilityUnit.KILOGRAM:
        return Decimal(quantity)
    if unit == TraceabilityUnit.METRIC_TONNE:
        return Decimal(quantity) * Decimal("1000")
    raise ValidationError({"quantity_unit": "Use kilograms or metric tonnes."})


def inventory_balances(batch, movements=None):
    if movements is None:
        movements = InventoryMovement.objects.filter(batch=batch).order_by(
            "movement_date",
            "created_at",
            "pk",
        )
    on_hand_kg = Decimal("0")
    reserved_kg = Decimal("0")
    for movement in movements:
        quantity_kg = quantity_to_kg(movement.quantity, movement.quantity_unit)
        if movement.movement_type in {
            InventoryMovement.MovementType.PRODUCTION_RECEIPT,
            InventoryMovement.MovementType.PROCESSING_INCREASE,
            InventoryMovement.MovementType.CORRECTION_IN,
        }:
            on_hand_kg += quantity_kg
        elif movement.movement_type in {
            InventoryMovement.MovementType.PROCESSING_DECREASE,
            InventoryMovement.MovementType.CORRECTION_OUT,
        }:
            on_hand_kg -= quantity_kg
        elif movement.movement_type == InventoryMovement.MovementType.RESERVATION:
            reserved_kg += quantity_kg
        elif movement.movement_type == InventoryMovement.MovementType.RESERVATION_RELEASE:
            reserved_kg -= quantity_kg
        elif movement.movement_type == InventoryMovement.MovementType.DISPATCH:
            on_hand_kg -= quantity_kg
            reserved_kg -= min(reserved_kg, quantity_kg)
    return on_hand_kg, reserved_kg
