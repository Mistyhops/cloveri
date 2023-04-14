from django.urls import path

from .views import NodeApiView, NodesApiView, RestoreNodeApiView

urlpatterns = [
    # get_tree
    path('v1/nodes/', NodesApiView.as_view()),
    # get_children
    path('v1/nodes/<int:pk>/', NodesApiView.as_view()),
    # create_node
    path('v1/node/', NodeApiView.as_view()),
    # get_node, #put_node, #delete_node
    path('v1/node/<int:pk>/', NodeApiView.as_view()),
    # restore_node
    path('v1/node/<int:pk>/restore/', RestoreNodeApiView.as_view()),
]
