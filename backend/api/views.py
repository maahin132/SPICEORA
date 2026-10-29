from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, ProductCategory


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
        categories = ProductCategory.objects.filter(
            is_active=True,
            products__is_published=True,
        ).distinct()
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
