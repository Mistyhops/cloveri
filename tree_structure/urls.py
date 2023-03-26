from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from tree_structure.views import NodeViewSet

router = DefaultRouter()
router.register(r'projects', NodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', TemplateView.as_view(
        template_name='documentation.html',
        extra_context={'schema_url': 'openapi/'}
    ), name='swagger-ui'),
    path('docs/openapi/', get_schema_view(
        title="Tree API",
    ), name='openapi-schema'),
]
