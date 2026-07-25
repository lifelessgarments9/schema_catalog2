from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from app.catalog.serializers import DeviceSerializer, CategorySerializer
from app.catalog.services import CatalogService
from app.catalog.models import Device


from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404


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
        params = request.query_params.dict()
        devices = CatalogService.get_all(filters=params or None)
        return Response(DeviceSerializer(devices, many=True, context={"request": request}).data)

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