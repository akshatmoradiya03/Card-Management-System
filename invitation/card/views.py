"""
Views for the cards app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Category, Tag, Card, CardImage
from .serializers import (
    CategorySerializer,
    TagSerializer,
    CardSerializer,
    CardCreateSerializer,
    CardListSerializer,
    CardImageSerializer,
)
from .filters import CardFilter


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category model.
    Provides CRUD operations for categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Tag model.
    Provides CRUD operations for tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Card model.
    Provides CRUD operations for cards with filtering and search.
    """
    queryset = Card.objects.select_related('category').prefetch_related('tags', 'images').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CardFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return CardCreateSerializer
        elif self.action == 'list':
            return CardListSerializer
        return CardSerializer

    def create(self, request, *args, **kwargs):
        """Create card with optional image uploads."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        card = serializer.save()
        
        # Handle image uploads if provided
        images = request.FILES.getlist('images')
        if images:
            uploaded_images = []
            for image_file in images:
                # Validate image format
                from .utils import validate_image_format, upload_to_s3
                try:
                    validate_image_format(image_file)
                    image_url = upload_to_s3(image_file, card.id)
                    card_image = CardImage.objects.create(card=card, image_url=image_url)
                    uploaded_images.append(CardImageSerializer(card_image).data)
                except Exception as e:
                    # If image upload fails, continue with other images
                    continue
            
            response_serializer = CardSerializer(card)
            response_data = response_serializer.data
            response_data['uploaded_images'] = uploaded_images
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        response_serializer = CardSerializer(card)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='upload-images')
    def upload_images(self, request, pk=None):
        """
        Upload multiple images for a card.
        
        POST /api/v1/cards/{id}/upload-images/
        Form Data: images=<file1>, images=<file2>, ...
        """
        card = self.get_object()
        images = request.FILES.getlist('images')
        
        if not images:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_images = []
        errors = []
        
        for idx, image_file in enumerate(images):
            try:
                from .utils import validate_image_format, upload_to_s3
                validate_image_format(image_file)
                image_url = upload_to_s3(image_file, card.id)
                card_image = CardImage.objects.create(card=card, image_url=image_url)
                uploaded_images.append(CardImageSerializer(card_image).data)
            except Exception as e:
                errors.append(f'Image {idx + 1}: {str(e)}')
        
        if uploaded_images:
            response_data = {
                'message': f'{len(uploaded_images)} image(s) uploaded successfully',
                'images': uploaded_images
            }
            if errors:
                response_data['errors'] = errors
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(
            {'error': 'Failed to upload images', 'details': errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'], url_path='images')
    def get_images(self, request, pk=None):
        """
        Get all images for a card.
        
        GET /api/v1/cards/{id}/images/
        """
        card = self.get_object()
        images = card.images.all()
        serializer = CardImageSerializer(images, many=True)
        return Response(serializer.data)


class CardImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for CardImage model (read-only).
    """
    queryset = CardImage.objects.select_related('card').all()
    serializer_class = CardImageSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['card']
    ordering_fields = ['uploaded_at']
    ordering = ['-uploaded_at']

