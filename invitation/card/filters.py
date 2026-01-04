"""
Filters for the cards app.
"""
import django_filters
from .models import Card, Category, Tag


class CardFilter(django_filters.FilterSet):
    """Filter for Card model."""
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags'
    )
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Card
        fields = ['category', 'tags', 'title']


