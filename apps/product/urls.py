"""
URL configuration for auking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, re_path, include
from .views import (
    IndexView, 
    DetailView, 
    ProductCategoryListView, 
    ProductSubCategoryListView,
    ProductSPUListView
)

###################################################################################################
###################################################################################################
###################################################################################################
###################################################################################################

urlpatterns = [
    re_path(r'^$', IndexView.as_view(), name='index'),                                                                                                          # Home page
    re_path(r'^product/(?P<productId>\d+)$', DetailView.as_view(), name='detail'),                                                                              # Product Detail
    re_path(r'^productcategory/(?P<categoryName>\w+)/(?P<page>\d+)$', ProductCategoryListView.as_view(), name='categoryList'),                                  # Category List page
    re_path(r'^productsubcategorylist/(?P<subCategoryName>[\w\s\'"+&-]+)/(?P<page>\d+)$', ProductSubCategoryListView.as_view(), name='subCategoryList'),         # SubCategory List page
    re_path(r'^productspulist/(?P<spuName>[\w\s\'"+-]+)/(?P<page>\d+)$', ProductSPUListView.as_view(), name='spuList'),                                         # SPU List page
]
