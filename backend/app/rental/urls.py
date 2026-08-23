from django.urls import path
from app.rental.views import RentalRequestView,CartView, RentalRequestPdfView

urlpatterns = [
    path("requests/", RentalRequestView.as_view(), name="rental-requests"),
    path("requests/<uuid:pk>/", RentalRequestView.as_view(), name="rental-request-detail"),
    path("cart/", CartView.as_view()),
    path("requests/<uuid:pk>/pdf/",RentalRequestPdfView.as_view(),name="rental-request-pdf"),
]