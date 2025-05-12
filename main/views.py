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





from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
import json

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")

            if not user_message:
                return JsonResponse({"error": "No message provided"}, status=400)

            headers = {
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
            }

            payload = {
                "model": "meta-llama/llama-3-8b-instruct:free",
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            }

            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()

            # Debug log
            print("OpenRouter raw response:", result)

            reply = result['choices'][0]['message']['content']
            return JsonResponse({"reply": reply})

        except requests.exceptions.HTTPError as http_err:
            print("HTTP Error:", http_err)
            print("Response content:", response.text)
            return JsonResponse({"error": "OpenRouter API HTTP Error", "details": response.text}, status=500)

        except Exception as e:
            import traceback
            print("Unhandled Error:", traceback.format_exc())
            return JsonResponse({"error": "Unhandled server error", "details": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)

