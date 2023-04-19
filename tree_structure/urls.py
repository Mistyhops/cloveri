from django.urls import path

from .views import NodeApiView, NodesApiView, DeleteRestoreNodeApiView

urlpatterns = [
    # get_tree
    path('v1/nodes/', NodesApiView.as_view()),
    # get_children
    path('v1/nodes/<int:pk>/', NodesApiView.as_view()),
    # create_node
    path('v1/node/', NodeApiView.as_view()),
    # get_node
    path('v1/node/<int:pk>/', NodeApiView.as_view()),

    # delete_node, restore_node
    path('v1/node/<int:pk>/hidden/', DeleteRestoreNodeApiView.as_view()),
]
