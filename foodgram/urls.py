from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.contrib.flatpages import views
from django.conf.urls.static import static

urlpatterns = [
    path("about/", include("django.contrib.flatpages.urls")),
    path('admin/', admin.site.urls),
    path('', include('recipes.urls')),
    path('auth/', include('users.urls')),
    path("auth/", include("django.contrib.auth.urls")),
]

urlpatterns += [
    path('about-author/', views.flatpage, {'url': '/about-author/'},
         name='about-author'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'},
         name='about-spec'),
]

handler404 = "recipes.views.page_not_found"
handler500 = "recipes.views.server_error"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
