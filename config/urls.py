from django.contrib import admin
from django.urls import path, include           # ← přidané include
from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        '',
        TemplateView.as_view(
            template_name='blueberry/Blueberry - eCommerce Tailwind CSS Template/blueberry-tailwind/index.html'
        ),
        name='home',
    ),

    path('blank/', TemplateView.as_view(template_name='pages/blank.html'), name='blank'),

    # shop (katalog)
    path('shop/', include('apps.catalog.urls', namespace='catalog')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path("checkout/", include("apps.checkout.urls", namespace="checkout")),
]

# DEV mapování pro Blueberry /assets/
urlpatterns += static(
    '/assets/',
    document_root=(
        settings.ROOT_DIR
        / 'static'
        / 'blueberry'
        / 'Blueberry - eCommerce Tailwind CSS Template'
        / 'blueberry-tailwind'
        / 'assets'
    ),
)
