# ===================================================================================================================
# 1. Tag-based filtering/search
# 2. Automatic table of content (toc)
# 3. Auto headings within the blog content
# 4. Related articles by tag / category
# 5. Author section
# 6. Image + metadata support
# ===================================================================================================================




from django.db import models
from django.utils.text import slugify

class BlogTag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f"#{self.name}"

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author_name = models.CharField(max_length=100)
    author_bio = models.CharField(max_length=255, blank=True)
    author_photo = models.ImageField(upload_to='authors/', blank=True, null=True)
    category = models.CharField(max_length=100)
    content = models.TextField(help_text="Use <h2> for subheadings to build Table of Contents")
    excerpt = models.TextField()
    tags = models.ManyToManyField(BlogTag)
    published_date = models.DateField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to="blog_thumbnails/", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
