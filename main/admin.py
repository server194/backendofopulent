from django.contrib import admin
from .models import BlogPost, BlogTag

@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'published_date']
    list_filter = ['category', 'tags', 'published_date']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['published_date']
