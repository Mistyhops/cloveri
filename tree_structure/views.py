from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from tree_structure.models import Node
from tree_structure.serializers import NodeSerializer, NewRootNodeSerializer, NewChildNodeSerializer


class NodeViewSet(viewsets.ModelViewSet):
    serializer_class = NodeSerializer
    queryset = Node.objects.all()

    @action(methods=['get'], detail=False)
    def get_tree(self, request):
        tree = Node.get_tree()
        serializer = NodeSerializer(tree, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def add_root(self, request):
        data = request.data
        serializer = NewRootNodeSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.validated_data['project_id']
        item_type = serializer.validated_data['item_type']
        item = serializer.validated_data['item']
        inner_order = serializer.validated_data.get('inner_order', 1)
        attributes = serializer.validated_data.get('attributes', None)

        root = Node.add_root(
            project_id=project_id,
            item_type=item_type,
            item=item,
            inner_order=inner_order,
            attributes=attributes
        )
        root_data = self.get_serializer(root).data
        return Response(root_data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True)
    def add_child(self, request, pk=None):
        parent = self.get_object()
        data = request.data

        if data.get('project_id', None) or data.get('item_type', None) or data.get('item', None):
            serializer = NewRootNodeSerializer(data=data)
        else:
            serializer = NewChildNodeSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        project_id = serializer.validated_data.get('project_id', None)
        item_type = serializer.validated_data.get('item_type', None)
        item = serializer.validated_data.get('item', None)
        attributes = serializer.validated_data.get('attributes')

        child = parent.add_child(
            project_id=project_id,
            item_type=item_type,
            item=item,
            attributes=attributes
        )
        child_data = self.get_serializer(child).data
        return Response(child_data, status=status.HTTP_201_CREATED)
