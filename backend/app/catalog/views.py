from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum

from app.catalog.serializers import DeviceSerializer, CategorySerializer
from app.catalog.services import CatalogService
from app.catalog.models import Device, Category


from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

class DevicePagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = "page_size"
    max_page_size = 50

class DeviceListView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]

    @extend_schema(
        responses=DeviceSerializer(many=True),
    )
    def get(self, request):
        params = {
            key: value
            for key, value in request.query_params.items()
            if key not in ("page", "page_size")
        }
        devices = CatalogService.get_all(filters=params or None)

        paginator = DevicePagination()
        page = paginator.paginate_queryset(devices, request)
        serializer = DeviceSerializer(page,many=True,context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        request=DeviceSerializer,
        responses={201: DeviceSerializer},
    )
    def post(self, request):
        serializer = DeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = CatalogService.create(serializer.validated_data) #serializer.validated_data будет изменен create
        return Response(DeviceSerializer(device, context={"request": request}).data, status=status.HTTP_201_CREATED)


class DeviceDetailView(APIView):

    def get_permissions(self):
        if self.request.method in ("PUT", "DELETE"):
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]

    @extend_schema(
        responses={200: DeviceSerializer},
    )
    def get(self, request, pk):
        device = get_object_or_404(Device, pk=pk)
        return Response(DeviceSerializer(device, context={"request": request}).data)

    @extend_schema(
        request=DeviceSerializer,
        responses={200: DeviceSerializer},
    )
    def put(self, request, pk):
        serializer = DeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device = CatalogService.update(
            pk,
            serializer.validated_data
        )
        return Response(DeviceSerializer(device, context={"request": request}).data)


    @extend_schema(
        responses={204: None},
    )
    def delete(self, pk):
        CatalogService.delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryView(APIView):
    @extend_schema(
        responses=CategorySerializer(many=True),
    )
    def get(self, request):
        categories = CatalogService.get_categories()
        return Response(CategorySerializer(categories, many=True, context={"request": request}).data)

class CatalogStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total = Device.objects.aggregate(total=Sum("quantity"))["total"] or 0

        available = Device.objects.filter(is_available=True,quantity__gt=0).count()

        categories = Category.objects.count()

        return Response({
            "total_devices": total,
            "available_devices": available,
            "categories": categories,
        })