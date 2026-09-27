from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # allauth (login / logout / signup via django-allauth)
    path("accounts/", include("allauth.urls")),

    # DRF token auth
    path("api/auth/", include("rest_framework.urls")),

    # App modules
    path("api/accounts/", include("app.accounts.urls")),
    path("api/", include("app.catalog.urls")),
    path("api/", include("app.rental.urls")),
    path("api/ai/", include("app.ai.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
