"""
Serializers for the cards app.
"""
from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import Category, Tag, Card, CardImage


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    cards_count = serializers.IntegerField(source='cards.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'cards_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    cards_count = serializers.IntegerField(source='cards.count', read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'cards_count', 'created_at']
        read_only_fields = ['created_at']


class CardImageSerializer(serializers.ModelSerializer):
    """Serializer for CardImage model."""
    class Meta:
        model = CardImage
        fields = ['id', 'image_url', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class CardSerializer(serializers.ModelSerializer):
    """Serializer for Card model."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        source='tags',
        write_only=True,
        required=False
    )
    images = CardImageSerializer(many=True, read_only=True)
    images_count = serializers.IntegerField(source='images.count', read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'title', 'description', 'category', 'category_id',
            'tags', 'tag_ids', 'images', 'images_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        """Validate that card title is unique within the same category."""
        title = attrs.get('title')
        category = attrs.get('category')
        
        if title and category:
            # Check for duplicate title in the same category
            existing_card = Card.objects.filter(
                title=title,
                category=category
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_card.exists():
                raise serializers.ValidationError({
                    'title': f'A card with this title already exists in the {category.name} category.'
                })
        
        return attrs


class CardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Card with multiple image uploads."""
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        source='tags',
        write_only=True,
        required=False
    )

    class Meta:
        model = Card
        fields = [
            'title', 'description', 'category_id', 'tag_ids'
        ]

    def validate(self, attrs):
        """Validate card data."""
        title = attrs.get('title')
        category = attrs.get('category')
        
        if title and category:
            # Check for duplicate title in the same category
            existing_card = Card.objects.filter(
                title=title,
                category=category
            )
            
            if existing_card.exists():
                raise serializers.ValidationError({
                    'title': f'A card with this title already exists in the {category.name} category.'
                })
        
        return attrs

    def create(self, validated_data):
        """Create card."""
        tags = validated_data.pop('tags', [])
        card = Card.objects.create(**validated_data)
        
        # Add tags
        if tags:
            card.tags.set(tags)
        
        return card


class CardListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Card list view."""
    category = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)
    images_count = serializers.IntegerField(source='images.count', read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'title', 'description', 'category', 'tags',
            'images_count', 'created_at', 'updated_at'
        ]

