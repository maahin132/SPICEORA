from decimal import Decimal

from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from .models import ExportEnquiry, Product, ProductCategory


def health(request):
    return JsonResponse({"status": "ok"})


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ("slug", "name")


class ProductListSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("slug", "name", "category", "summary", "image", "image_alt")

    def get_image(self, product):
        if not product.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(product.image.url)
        return product.image.url


class ProductDetailSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ("description",)


class ProductPagination(PageNumberPagination):
    page_size = 12


class PublicCatalogView(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def invalid_parameters(request, allowed):
        errors = {
            key: ["Unknown query parameter."]
            for key in sorted(set(request.query_params) - allowed)
        }
        repeated = {
            key
            for key in request.query_params
            if len(request.query_params.getlist(key)) > 1
        }
        errors.update(
            {key: ["Provide this query parameter only once."] for key in repeated}
        )
        if errors:
            return Response(
                {"errors": errors},
                status=400,
            )
        return None


class ProductCategoryListView(PublicCatalogView):
    def get(self, request):
        invalid = self.invalid_parameters(request, set())
        if invalid:
            return invalid
        categories = ProductCategory.objects.filter(is_active=True)
        return Response(ProductCategorySerializer(categories, many=True).data)


class ProductListView(PublicCatalogView):
    def get(self, request):
        invalid = self.invalid_parameters(request, {"category", "page"})
        if invalid:
            return invalid

        page_number = request.query_params.get("page")
        if "page" in request.query_params and (
            not page_number
            or not page_number.isascii()
            or not page_number.isdecimal()
            or len(page_number) > 9
            or int(page_number) < 1
        ):
            return Response(
                {"errors": {"page": ["Enter a positive page number."]}},
                status=400,
            )

        products = Product.objects.filter(
            is_published=True,
            category__is_active=True,
        ).select_related("category")
        category_slug = request.query_params.get("category")
        if "category" in request.query_params and not category_slug:
            return Response(
                {"errors": {"category": ["A category slug is required."]}},
                status=400,
            )
        if category_slug:
            if not ProductCategory.objects.filter(
                slug=category_slug,
                is_active=True,
            ).exists():
                return Response(
                    {"errors": {"category": ["Unknown or inactive category."]}},
                    status=400,
                )
            products = products.filter(category__slug=category_slug)

        paginator = ProductPagination()
        page = paginator.paginate_queryset(products, request, view=self)
        serializer = ProductListSerializer(
            page,
            many=True,
            context={"request": request},
        )
        return paginator.get_paginated_response(serializer.data)


class ProductDetailView(PublicCatalogView):
    def get(self, request, slug):
        invalid = self.invalid_parameters(request, set())
        if invalid:
            return invalid
        product = get_object_or_404(
            Product.objects.select_related("category"),
            slug=slug,
            is_published=True,
            category__is_active=True,
        )
        serializer = ProductDetailSerializer(
            product,
            context={"request": request},
        )
        return Response(serializer.data)


class PublicEnquiryRateThrottle(SimpleRateThrottle):
    scope = "public_enquiry"

    def get_rate(self):
        try:
            return api_settings.DEFAULT_THROTTLE_RATES[self.scope]
        except KeyError as error:
            raise ImproperlyConfigured(
                f"Rate for scope {self.scope!r} is not configured."
            ) from error

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


class ExportEnquiryCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=120)
    company_name = serializers.CharField(
        max_length=160,
        required=False,
        allow_blank=True,
    )
    email = serializers.EmailField(max_length=254)
    phone = serializers.CharField(max_length=40, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100)
    category_slug = serializers.SlugField(max_length=100, required=False)
    product_slug = serializers.SlugField(max_length=150, required=False)
    quantity = serializers.DecimalField(
        max_digits=16,
        decimal_places=3,
        min_value=Decimal("0.001"),
    )
    quantity_unit = serializers.ChoiceField(
        choices=ExportEnquiry.QuantityUnit.choices,
    )
    message = serializers.CharField(
        max_length=5000,
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        product_slug = attrs.pop("product_slug", None)
        category_slug = attrs.pop("category_slug", None)
        if bool(product_slug) == bool(category_slug):
            raise serializers.ValidationError(
                {
                    "category_slug": [
                        "Select one active category or one published product."
                    ]
                }
            )

        product = None
        if product_slug:
            product = Product.objects.select_related("category").filter(
                slug=product_slug,
                is_published=True,
                category__is_active=True,
            ).first()
            if product is None:
                raise serializers.ValidationError(
                    {"product_slug": ["Select a published product."]}
                )
            category = product.category
        else:
            category = ProductCategory.objects.filter(
                slug=category_slug,
                is_active=True,
            ).first()
            if category is None:
                raise serializers.ValidationError(
                    {"category_slug": ["Select an active category."]}
                )

        attrs["category"] = category
        attrs["product"] = product
        attrs["product_name_snapshot"] = product.name if product else ""
        return attrs


class ExportEnquiryCreateView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (PublicEnquiryRateThrottle,)

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response(
                {"errors": {"non_field_errors": ["Submit a JSON object."]}},
                status=400,
            )
        serializer = ExportEnquiryCreateSerializer(data=request.data)
        unknown_fields = set(request.data) - set(serializer.fields)
        if unknown_fields:
            return Response(
                {
                    "errors": {
                        field: ["Unknown field."]
                        for field in sorted(unknown_fields)
                    }
                },
                status=400,
            )
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=400)
        enquiry = self._create_enquiry(serializer.validated_data)
        return Response(
            {
                "reference": str(enquiry.public_reference),
                "message": "Your enquiry has been received.",
            },
            status=201,
        )

    @staticmethod
    @transaction.atomic
    def _create_enquiry(validated_data):
        return ExportEnquiry.objects.create(**validated_data)
