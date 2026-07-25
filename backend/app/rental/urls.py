from django.urls import path
from app.rental.views import RentalRequestView,CartView

urlpatterns = [
    path("requests/", RentalRequestView.as_view(), name="rental-requests"),
    path("requests/<int:pk>/", RentalRequestView.as_view(), name="rental-request-detail"),
    path("cart/", CartView.as_view()),
]