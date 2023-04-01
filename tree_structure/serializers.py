from rest_framework import serializers

from .models import Node


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'


class NewNodeSerializer(serializers.ModelSerializer):

    attributes = serializers.JSONField(read_only=True)
    id = serializers.JSONField(read_only=True)
    path = serializers.JSONField(read_only=True)


    class Meta:
        model = Node
        fields = ('id', 'path', 'project_id', 'item_type', 'item', 'inner_order', 'attributes', )


