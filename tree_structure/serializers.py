from rest_framework import serializers

from tree_structure.models import Node


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'


class NewRootNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ('project_id', 'item_type', 'item', 'attributes', )


class NewChildNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ('attributes', )
