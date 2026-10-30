import uuid

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q


def validate_image_size(image):
    if image.size > 5 * 1024 * 1024:
        raise ValidationError("Product images must be 5 MB or smaller.")


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
        upload_to="products/",
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=("jpg", "jpeg", "png", "webp")),
            validate_image_size,
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
        on_delete=models.SET_NULL,
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
