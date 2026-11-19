from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
URL_PREFIX = f"{settings.APP_URL_PREFIX}/" if settings.APP_URL_PREFIX else ""

urlpatterns = [
    path(f"{URL_PREFIX}admin/", admin.site.urls),

    path(f"{URL_PREFIX}accounts/", include("app.accounts.urls")),
    path(f"{URL_PREFIX}catalog/", include("app.catalog.urls")),
    path(f"{URL_PREFIX}rental/", include("app.rental.urls")),
    path(f"{URL_PREFIX}ai/", include("app.ai.urls")),

    # OpenAPI schema
    path(f"{URL_PREFIX}api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        f"{URL_PREFIX}swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)