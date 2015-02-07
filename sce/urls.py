from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sce.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^sceapp/', include('sceapp.urls', namespace="sceapp")),
    url(r'^admin/', include(admin.site.urls)),
)
