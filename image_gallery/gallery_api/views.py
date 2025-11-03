from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import ImageItem
from .serializers import RegisterSerializer, ImageItemSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .llm_services import generate_caption_for_image
from .serializers import UserSerializer

User = get_user_model()

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ImageListCreateView(generics.ListCreateAPIView):
    serializer_class = ImageItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # Add support for form data

    def get_queryset(self):
        # global list or filter by ?owner=
        owner = self.request.query_params.get("owner", None)
        qs = ImageItem.objects.all()
        if owner == "me":
            qs = qs.filter(owner=self.request.user)
        # support search by caption keyword
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(caption__icontains=q)
        return qs

    def get_serializer_context(self):
        """Add request to serializer context for proper URL generation"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        # Get authenticated user details
        user = request.user
        user_data = UserSerializer(user).data
        
        # Handle the incoming form data
        image = request.FILES.get('image')
        if not image:
            return Response(
                {'error': 'No image file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create serializer with manual data dict
        data = {
            'image': image,
            'caption': request.data.get('caption', ''),  # Optional caption
        }
        
        # Pass request in context for proper URL generation
        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        
        # Generate caption using LLM if no caption provided
        if not data['caption'] and instance and instance.image:
            try:
                generated_caption = generate_caption_for_image(instance.image.path)
                instance.caption = generated_caption
                instance.is_captioned = True
                instance.save()
                # Refresh serializer data to include the generated caption
                serializer = self.get_serializer(instance, context={'request': request})
            except Exception as e:
                # If caption generation fails, log it but don't fail the upload
                print(f"Caption generation failed: {str(e)}")
        
        response_data = {
            'image': serializer.data,
            'user': user_data
        }
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        f = self.request.FILES.get("image")
        instance = serializer.save(
            owner=self.request.user,
            original_filename=f.name if f else ""
        )
        return instance  # Return the instance for caption generation

class ImageRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ImageItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ImageItem.objects.all()

    def perform_update(self, serializer):
        # only owner can edit caption
        instance = self.get_object()
        if instance.owner != self.request.user:
            raise PermissionDenied("Not owner")
        serializer.save()

class MyImagesListView(generics.ListAPIView):
    serializer_class = ImageItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['caption']  # Fields to search in
    filterset_fields = {
        "uploaded_at": ["exact", "gte", "lte"],  # date/time filtering
    }
    
    def get_queryset(self):
        queryset = ImageItem.objects.filter(owner=self.request.user)
        return queryset.order_by('-uploaded_at')  # Latest first
    
    def get_serializer_context(self):
        """Add request to serializer context for proper URL generation"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def list(self, request, *args, **kwargs):
        # Get user details
        user = request.user
        
        # Get paginated and filtered images list
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Get pagination data
            pagination_data = {
                'count': self.paginator.count,
                'images': serializer.data
            }
            images_data = pagination_data
        else:
            serializer = self.get_serializer(queryset, many=True)
            images_data = serializer.data
        
        return Response(images_data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_caption_view(request, pk):
    img = get_object_or_404(ImageItem, pk=pk)
    if img.owner != request.user:
        return Response({"detail":"Not allowed"}, status=403)
    # call the captioning service synchronously (blocking)
    caption = generate_caption_for_image(img.image.path)
    img.caption = caption
    img.is_captioned = True
    img.save()
    return Response({"id": img.id, "caption": caption})
