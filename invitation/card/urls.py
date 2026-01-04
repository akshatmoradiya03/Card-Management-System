from django.urls import path, include
from rest_framework.routers import DefaultRouter
from card.views import CategoryViewSet, TagViewSet, CardViewSet, CardImageViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('tags', TagViewSet)
router.register('cards', CardViewSet)
router.register('card-images', CardImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
