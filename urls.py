
from django.conf import settings
from django.conf.urls.static import static

urlpattenrs = [
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        ]
