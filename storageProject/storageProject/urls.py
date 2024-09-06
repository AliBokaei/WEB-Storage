from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    path('login/', include('login.urls')),
    path('register/', include('register.urls')),
    path('home/', include('storage.urls')),
    path('accounts/', include('allauth.urls')),
    # path('upload/', views.upload_view, name='upload'),
    path('upload/', include('upload.urls'))
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
