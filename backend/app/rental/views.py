from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from app.catalog.serializers import DeviceSerializer
from app.rental.models import RentalRequest
from app.rental.serializers import RentalRequestSerializer
from app.rental.services import CartService, RentalRequestService


class RentalRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        qs = RentalRequestService.get_requests(request.user)
        return Response(RentalRequestSerializer(qs, many=True).data)

    def get(self, request, pk=None):
        if pk is None:
            qs = RentalRequestService.get_requests(request.user)
            return Response(
                RentalRequestSerializer(qs, many=True).data
            )

        rental = RentalRequest.objects.get(pk=pk)

        if not request.user.is_staff and rental.student != request.user:
            return Response(status=403)

        return Response(
            RentalRequestSerializer(rental).data
        )

    def post(self, request):
        serializer = RentalRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rental = RentalRequestService.create(
            student=request.user,
            data=serializer.validated_data,
        )
        return Response(RentalRequestSerializer(rental).data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        try:
            rental = RentalRequestService.approve(pk)
            return Response(RentalRequestSerializer(rental).data)
        except RentalRequest.DoesNotExist:
            return Response({"error": "Заявка не найдена."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            RentalRequestService.delete(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except RentalRequest.DoesNotExist:
            return Response({"error": "Заявка не найдена."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            rental = RentalRequestService.return_devices(pk)
            return Response(RentalRequestSerializer(rental).data)
        except RentalRequest.DoesNotExist:
            return Response(
                {"error": "Заявка не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        devices = CartService.get(request.user.id)
        return Response(DeviceSerializer(devices, many=True, context={"request": request}).data)

    def post(self, request):
        device_id = request.data.get("device")
        if not device_id:
            return Response({"error": "device обязателен."}, status=status.HTTP_400_BAD_REQUEST)
        devices = CartService.add(request.user.id, int(device_id))
        return Response(DeviceSerializer(devices, many=True, context={"request": request}).data)

    def delete(self, request):
        device_id = request.data.get("device")
        if not device_id:
            return Response({"error": "device обязателен."}, status=status.HTTP_400_BAD_REQUEST)
        devices = CartService.remove(request.user.id, int(device_id))
        return Response(DeviceSerializer(devices, many=True, context={"request": request}).data)