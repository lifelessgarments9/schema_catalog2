from django.urls import path

from app.catalog.views import DeviceListView, DeviceDetailView, CategoryView

urlpatterns = [
    path("devices/", DeviceListView.as_view()),
    path("devices/<int:pk>/", DeviceDetailView.as_view()),
    path("categories/", CategoryView.as_view()),

]