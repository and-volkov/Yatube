from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path  # sorted import

urlpatterns = [
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    path('', include('posts.urls', namespace='posts')),  # changed order
    path('admin/', admin.site.urls),
]

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.permission_denied'
handler403csrf = 'core.views.csrf_failure'
handler500 = 'core.views.server_error'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )