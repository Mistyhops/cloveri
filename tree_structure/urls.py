from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tree_structure.views import NodeViewSet

router = DefaultRouter()
router.register(r'projects', NodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
