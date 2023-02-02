"""
djangodemo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

# def sentry_debug(request):
# 	# trigger error
#     division_by_zero = 1 / 0


urlpatterns = [
    # admin urls
    path("admin/", admin.site.urls),
    # sentry debug url
    # path('sentry-debug/', sentry_debug),
    # redirect home to admin until the website pages will be ready
    path("", RedirectView.as_view(url="admin/"), name="home"),
    path("", include("robocjk.api.urls")),
    # media and static files with keycdn
    # https://www.keycdn.com/support/django-cdn-integration
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
            "show_indexes": True,
        },
    ),
    re_path(
        r"^static/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.STATIC_ROOT,
            "show_indexes": True,
        },
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
