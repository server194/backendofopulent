from . models import * 
from rest_framework import serializers


# BlogTagSerializer
class BlogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ['id', 'name']


# BlogPostListSerializer
class BlogPostListSerializer(serializers.ModelSerializer):
    tags = BlogTagSerializer(many=True, read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'category', 'published_date',
            'thumbnail', 'tags'
        ]


# BlogPostDetailSerializer
class BlogPostDetailSerializer(serializers.ModelSerializer):
    tags = BlogTagSerializer(many=True, read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'author_name', 'author_bio', 'author_photo',
            'category', 'content', 'excerpt', 'tags',
            'published_date', 'thumbnail'
        ]


# BlogPostCreateSerializer
class BlogPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'

    def validate_content(self, value):
        from .utils import convert_plaintext_to_html
        return convert_plaintext_to_html(value)

class BlogBlockSerializer(serializers.Serializer):
    type = serializers.CharField()
    text = serializers.CharField()

class BlogPostStructuredSerializer(serializers.ModelSerializer):
    blocks = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'blocks', 'published_date', 'author_name', 'author_bio', 'thumbnail', 'tags']

    def get_blocks(self, obj):
        lines = obj.content.splitlines()
        blocks = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("📘"):
                blocks.append({"type": "heading", "text": line[2:].strip()})
            elif (
                line.istitle() and
                not line.endswith('.') and
                len(line) <= 60
            ):
                blocks.append({"type": "subheading", "text": line})
            else:
                blocks.append({"type": "paragraph", "text": line})
        return blocks











# ========================================================================================================================================================================================
# Serializers>	Purpose	Used In View
# BlogPostListSerializer	>For home/blog cards -->	BlogPostListAPIView, BlogTagSearchView
# BlogPostDetailSerializer >	For full content/detail view -->	BlogPostDetailAPIView, RelatedBlogAPIView
# BlogTagSerializer >	Reused inside blog serializers	All 
# BlogPostCreateSerializer >	Admin-side create/edit (optional) -->	CreateAPIView, UpdateAPIView
# ========================================================================================================================================================================================