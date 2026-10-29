from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


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
