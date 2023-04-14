from django.contrib import admin
from django.urls import path, include
import notifications.urls


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path("", include('books.urls')),
    path('__debug__/', include('debug_toolbar.urls'))
]

