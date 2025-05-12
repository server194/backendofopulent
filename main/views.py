from django.shortcuts import render
import re
from .models import *
from .serializers import *
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response


# 1. List All Blog Posts (for home or blog listing page)
class BlogPostListAPIView(generics.ListAPIView):
    queryset = BlogPost.objects.all().order_by('-published_date')
    serializer_class = BlogPostListSerializer  
    

# 2. Get Blog Post Detail by Slug
class BlogPostDetailAPIView(generics.RetrieveAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer  
    lookup_field = "slug"


# 3. Extract Table of Contents (optional function if needed)
def extract_toc(html_content):
    headings = re.findall(r'<h2[^>]*>(.*?)</h2>', html_content)
    return headings


# 4. Get Related Articles by Tags
# class RelatedBlogAPIView(generics.ListAPIView):
#     serializer_class = BlogPostListSerializer 
#     def get_queryset(self):
#         slug = self.kwargs['slug']
#         try:
#             current_post = BlogPost.objects.get(slug=slug)
#             return BlogPost.objects.filter(tags__in=current_post.tags.all()) \
#                 .exclude(id=current_post.id).distinct()[:4]
#         except BlogPost.DoesNotExist:
#             return BlogPost.objects.none()
class RelatedBlogAPIView(generics.ListAPIView):
    serializer_class = BlogPostListSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        try:
            post = BlogPost.objects.get(slug=slug)
            return BlogPost.objects.filter(
                models.Q(tags__in=post.tags.all()) | models.Q(category=post.category)
            ).exclude(id=post.id).distinct()[:4]
        except BlogPost.DoesNotExist:
            return BlogPost.objects.none()



# 5. Search Posts by Tag
class BlogTagSearchView(generics.ListAPIView):
    serializer_class = BlogPostListSerializer  
    
    def get_queryset(self):
        tag = self.kwargs['tag']
        return BlogPost.objects.filter(tags__name__iexact=tag)


# 6. Search by Title / Content
class BlogPostSearchView(generics.ListAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostListSerializer 
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'excerpt']




#  Create Blog Post (admin only or staff)
class BlogPostCreateAPIView(generics.CreateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostCreateSerializer
    permission_classes = [AllowAny]  # Only staff/admin can create



class BlogPostUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostCreateSerializer
    lookup_field = "slug"
    permission_classes = [AllowAny]

class BlogPostDeleteAPIView(generics.DestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostCreateSerializer
    lookup_field = "slug"
    permission_classes = [AllowAny]



class BlogPostTOCAPIView(APIView):
    def get(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug)
            # Extract both h2 and h3 headings with their level
            matches = re.findall(r'<(h[2-3])[^>]*>(.*?)</\1>', post.content)
            toc = [{"level": level, "text": text.strip()} for level, text in matches]
            return Response({"toc": toc})
        except BlogPost.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)
        
class BlogPostStructuredDetailAPIView(generics.RetrieveAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostStructuredSerializer
    lookup_field = "slug"





import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "openrouter/auto",  # or a specific model like "openrouter/gpt-4"
            "messages": [
                {"role": "user", "content": user_message}
            ],
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        try:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            return JsonResponse({"reply": reply})
        except Exception as e:
            return JsonResponse({"error": "Failed to get response", "details": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)
