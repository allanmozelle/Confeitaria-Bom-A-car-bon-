from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('principal.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('produtos/', include('produtos.urls')),
    path('pedidos/', include('pedidos.urls')),
]

# Em desenvolvimento, serve as imagens enviadas (pasta media/).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
