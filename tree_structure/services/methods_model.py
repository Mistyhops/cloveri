
from ..models import Node
from ..serializers import NodeSerializer, NewNodeSerializer
from rest_framework.generics import get_object_or_404

def get_node(pk):
    """Метод вывода записи из модели Node"""
    try:
        result = NodeSerializer(Node.objects.get(pk=pk), many=False).data
        return result
    except:
        return None
    # result = NodeSerializer(Node.objects.all(), many=True).data

def get_nodes(pk):
    """Метод вывода записи из модели Node"""
    try:
        instance = Node.objects.get(pk=pk)
        path = instance.path
        path += '0' * (10 - len(str(instance.id))) + str(instance.id)
        result = NodeSerializer(Node.objects.filter(path__startswith=path), many=True).data
        return result
    except:
        return None


def create_node(request):
    """Метод создания нового узла в модели Node"""
    serializer = NewNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    #здесь остается вопрос, как валидировать project_id, если parent_id не передаем
    #и создаем корневой узел. Теоритически project_id не должен продублироваться

    try:
        parent_id = request.data['parent_id']
        parent = Node.objects.get(id=parent_id)
        path = parent.path
        path += '0' * (10 - len(str(parent.id))) + str(parent.id)
        num_child = Node.objects.filter(path=path)
        inner_order = len(num_child) + 1
    except KeyError:
        path = ""
        inner_order = 1

    try:
        node_new = Node.objects.create(
            path=path,
            project_id=request.data['project_id'],
            item_type=request.data['item_type'],
            item=request.data['item'],
            inner_order=inner_order,
            attributes=request.data['attributes'],
        )
        return NewNodeSerializer(node_new).data
    except:
        return None


def update_attributes_node(request, pk):
    serializer = NewNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        instance = Node.objects.get(pk=pk)
        instance.attributes = request.data['attributes']
        instance.save()
        return NewNodeSerializer(instance).data
    except:
        return None





