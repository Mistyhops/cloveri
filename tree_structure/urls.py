from django.urls import path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from .views import NodeApiView, NodesApiView

urlpatterns = [
    #get_tree
    path('v1/nodes/', NodesApiView.as_view()),
    #get_children
    path('v1/nodes/<int:pk>/', NodesApiView.as_view()),
    #create_node
    path('v1/node/', NodeApiView.as_view()),
    #get_node, #put_node, #delete_node
    path('v1/node/<int:pk>/', NodeApiView.as_view()),
]
