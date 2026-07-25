from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [

    path("admin/", admin.site.urls),

    path("accounts/", include("app.accounts.urls")),
    path("catalog/", include("app.catalog.urls")),
    path("rental/", include("app.rental.urls")),
    path("ai/", include("app.ai.urls")),

    # OpenAPI schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)