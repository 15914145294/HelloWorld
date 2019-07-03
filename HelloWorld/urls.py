"""HelloWorld URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from . import view, testdb, search, search2
from django.conf.urls import *
from django.contrib import admin

urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^hello/$', view.hello),
	url(r'^testdb/$', testdb.testdb),
	url(r'^test_query/$', testdb.test_query),
	url(r'^test_update/$', testdb.test_update),
	url(r'^test_delete/$', testdb.test_delete),
	url(r'^search_form', search.search_form),
	url(r'^search$', search.search),
	url(r'^search-post$', search2.search_post),
]
