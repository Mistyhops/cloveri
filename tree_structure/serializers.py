from rest_framework import serializers

from .models import Node


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ('id', 'path', 'project_id', 'item_type', 'item', 'inner_order', 'attributes')


class NewNodeSerializer(serializers.ModelSerializer):
    path = serializers.CharField(read_only=True)
    inner_order = serializers.IntegerField(read_only=True)

    class Meta:
        model = Node
        fields = ('id', 'path', 'project_id', 'item_type', 'item', 'inner_order', 'attributes')
