"""
Admin configuration for cards app.
"""
from django.contrib import admin
from .models import Category, Tag, Card, CardImage


class CardImageInline(admin.TabularInline):
    """Inline admin for CardImage model."""
    model = CardImage
    extra = 1
    fields = ('id','image_url', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    list_display = ('id', 'name', 'description', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag model."""
    list_display = ('id','name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    """Admin configuration for Card model."""
    list_display = ('id','title', 'category', 'created_at', 'updated_at')
    list_filter = ('category', 'tags', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CardImageInline]


@admin.register(CardImage)
class CardImageAdmin(admin.ModelAdmin):
    """Admin configuration for CardImage model."""
    list_display = ('id','card', 'image_url', 'uploaded_at')
    list_filter = ('uploaded_at', 'card__category')
    search_fields = ('card__title', 'image_url')
    readonly_fields = ('uploaded_at',)


