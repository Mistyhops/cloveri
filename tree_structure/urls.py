from django.urls import path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from .views import GetNodesApiView, NodeApiView



urlpatterns = [
    path('v1/nodes/', GetNodesApiView.as_view()),
    path('v1/node/', NodeApiView.as_view()),

    path('docs/', TemplateView.as_view(
        template_name='documentation.html',
        extra_context={'schema_url': 'openapi/'}
    ), name='swagger-ui'),
    path('docs/openapi/', get_schema_view(
        title="Tree API",
    ), name='openapi-schema'),
]
