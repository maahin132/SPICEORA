from decimal import Decimal

from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAdminUser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

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


def model_validation_errors(error):
    try:
        return error.message_dict
    except AttributeError:
        return {"non_field_errors": error.messages}


class OperationsModelSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        instance = self.instance or self.Meta.model()
        for field, value in attrs.items():
            setattr(instance, field, value)
        try:
            instance.full_clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                model_validation_errors(error)
            ) from error
        return attrs


class FarmSerializer(OperationsModelSerializer):
    class Meta:
        model = Farm
        fields = (
            "reference",
            "name",
            "location",
            "area",
            "area_unit",
            "description",
            "internal_notes",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class CropSeasonSerializer(OperationsModelSerializer):
    farm_reference = serializers.SlugRelatedField(
        source="farm",
        slug_field="reference",
        queryset=Farm.objects.all(),
    )

    class Meta:
        model = CropSeason
        fields = (
            "reference",
            "farm_reference",
            "crop_name",
            "planting_date",
            "expected_harvest_date",
            "status",
            "internal_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class HarvestSerializer(OperationsModelSerializer):
    crop_season_reference = serializers.SlugRelatedField(
        source="crop_season",
        slug_field="reference",
        queryset=CropSeason.objects.all(),
    )

    class Meta:
        model = Harvest
        fields = (
            "reference",
            "crop_season_reference",
            "harvest_date",
            "quantity",
            "quantity_unit",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class ProductionBatchSerializer(OperationsModelSerializer):
    harvest_reference = serializers.SlugRelatedField(
        source="harvest",
        slug_field="reference",
        queryset=Harvest.objects.all(),
    )
    crop_season_reference = serializers.SerializerMethodField()
    farm_reference = serializers.SerializerMethodField()
    available_quantity_kg = serializers.SerializerMethodField()

    class Meta:
        model = ProductionBatch
        fields = (
            "reference",
            "harvest_reference",
            "crop_season_reference",
            "farm_reference",
            "product_name",
            "batch_date",
            "initial_quantity",
            "quantity_unit",
            "status",
            "internal_notes",
            "available_quantity_kg",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "crop_season_reference",
            "farm_reference",
            "available_quantity_kg",
            "created_at",
            "updated_at",
        )

    def get_crop_season_reference(self, batch):
        return batch.harvest.crop_season.reference

    def get_farm_reference(self, batch):
        return batch.harvest.crop_season.farm.reference

    def get_available_quantity_kg(self, batch):
        from .models import inventory_balances

        on_hand_kg, reserved_kg = inventory_balances(batch)
        return format(on_hand_kg - reserved_kg, "f")


class ProcessingRecordSerializer(OperationsModelSerializer):
    batch_reference = serializers.SlugRelatedField(
        source="batch",
        slug_field="reference",
        queryset=ProductionBatch.objects.all(),
    )

    class Meta:
        model = ProcessingRecord
        fields = (
            "id",
            "batch_reference",
            "activity",
            "activity_date",
            "input_quantity",
            "input_unit",
            "output_quantity",
            "output_unit",
            "description",
            "supporting_document_references",
            "internal_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class InventoryMovementSerializer(OperationsModelSerializer):
    batch_reference = serializers.SlugRelatedField(
        source="batch",
        slug_field="reference",
        queryset=ProductionBatch.objects.all(),
    )
    class Meta:
        model = InventoryMovement
        fields = (
            "reference",
            "batch_reference",
            "movement_type",
            "quantity",
            "quantity_unit",
            "movement_date",
            "reason",
            "internal_notes",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def validate(self, attrs):
        movement_type = attrs.get(
            "movement_type",
            getattr(self.instance, "movement_type", None),
        )
        request = self.context.get("request")
        correction_types = {
            InventoryMovement.MovementType.CORRECTION_IN,
            InventoryMovement.MovementType.CORRECTION_OUT,
        }
        if (
            movement_type in correction_types
            and request
            and not request.user.has_perm("api.approve_inventory_correction")
        ):
            raise PermissionDenied(
                "You need correction-approval permission to record this movement."
            )
        return super().validate(attrs)



class OperationsPagination(PageNumberPagination):
    page_size = 25


class StaffModelPermissions(DjangoModelPermissions):
    perms_map = {
        **DjangoModelPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
    }


class ProtectedOperationsCollectionView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAdminUser, StaffModelPermissions)
    pagination_class = OperationsPagination
    queryset = None
    serializer_class = None

    def get_queryset(self):
        return self.queryset.all()

    def get(self, request):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(
            page,
            many=True,
            context={"request": request},
        )
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not isinstance(request.data, dict):
            return Response(
                {"errors": {"non_field_errors": ["Submit a JSON object."]}},
                status=400,
            )
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
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
        try:
            instance = serializer.save()
        except DjangoValidationError as error:
            return Response(
                {"errors": model_validation_errors(error)},
                status=400,
            )
        return Response(
            self.serializer_class(instance, context={"request": request}).data,
            status=201,
        )


class FarmOperationsView(ProtectedOperationsCollectionView):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer


class CropSeasonOperationsView(ProtectedOperationsCollectionView):
    queryset = CropSeason.objects.select_related("farm")
    serializer_class = CropSeasonSerializer


class HarvestOperationsView(ProtectedOperationsCollectionView):
    queryset = Harvest.objects.select_related("crop_season")
    serializer_class = HarvestSerializer


class ProductionBatchOperationsView(ProtectedOperationsCollectionView):
    queryset = ProductionBatch.objects.select_related(
        "harvest__crop_season__farm"
    )
    serializer_class = ProductionBatchSerializer


class ProcessingRecordOperationsView(ProtectedOperationsCollectionView):
    queryset = ProcessingRecord.objects.select_related("batch")
    serializer_class = ProcessingRecordSerializer


class InventoryMovementOperationsView(ProtectedOperationsCollectionView):
    queryset = InventoryMovement.objects.select_related("batch")
    serializer_class = InventoryMovementSerializer
