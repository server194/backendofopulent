"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from main.views import BlogPostStructuredDetailAPIView
from main.views import (
    BlogPostListAPIView,
    BlogPostDetailAPIView,
    RelatedBlogAPIView,
    BlogTagSearchView,
    BlogPostSearchView,
    BlogPostCreateAPIView,
    BlogPostUpdateAPIView,
    BlogPostDeleteAPIView,
    BlogPostTOCAPIView,
    chat_view,
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/blogs/", BlogPostListAPIView.as_view(), name="blog-list"),
    path("api/blogs/<slug:slug>/", BlogPostDetailAPIView.as_view(), name="blog-detail"),
    path("api/blogs/<slug:slug>/related/", RelatedBlogAPIView.as_view(), name="blog-related"),
    path("api/blogs/<slug:slug>/toc/", BlogPostTOCAPIView.as_view(), name="blog-toc"),
    path("api/blogs/tag/<str:tag>/", BlogTagSearchView.as_view(), name="blog-tag-search"),
    path("api/blogs/search/", BlogPostSearchView.as_view(), name="blog-search"),
    path("api/blogs/create/", BlogPostCreateAPIView.as_view(), name="blog-create"),
    path("api/blogs/<slug:slug>/edit/", BlogPostUpdateAPIView.as_view(), name="blog-update"),
    path("api/blogs/<slug:slug>/delete/", BlogPostDeleteAPIView.as_view(), name="blog-delete"),
    
    path("blogs/<slug:slug>/structured/", BlogPostStructuredDetailAPIView.as_view()),

    path('api/chat/', chat_view, name='chat'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)