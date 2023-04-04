from rest_framework.exceptions import ValidationError

from ..models import Node
from ..serializers import NodeSerializer, NewNodeSerializer

from .validate_fields_model import Validate

def get_tree():
    """Метод вывода всех узлов из модели Node"""
    result = NodeSerializer(Node.objects.all(), many=True).data
    return result


def get_node(pk):
    """Метод вывода узла из модели Node"""
    # get_objects_or_404
    serializer = NodeSerializer(Node.objects.get(pk=pk), many=False).data
    serializer.is_valid(raise_exception=True)
    return serializer


def get_children(pk):
    """Метод вывода всех дочерних узлов из модели Node"""
    instance = Node.objects.get(pk=pk)
    path = instance.path
    path += '0' * (10 - len(str(instance.id))) + str(instance.id)
    result = NodeSerializer(Node.objects.filter(path__startswith=path), many=True).data
    return result


def create_node(request):
    """Метод создания нового узла в модели Node"""
    fields_val = [
        'project_id',
        'item_type',
        'item',
        'attributes',
    ]
    validate = Validate(request.data, *fields_val)
    validate.validate_fields_required()


    serializer = NewNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    #здесь остается вопрос, как валидировать project_id, если parent_id не передаем
    #и создаем корневой узел. Теоритически project_id не должен продублироваться

    try:
        parent_id = request.data['parent_id']
        parent = validate.validate_parent_id_value(parent_id)
        path = parent.path
        path += '0' * (10 - len(str(parent.id))) + str(parent.id)
        num_child = Node.objects.filter(path=path)
        inner_order = len(num_child) + 1
    except KeyError:
        path = ""
        inner_order = 1


    node_new = Node.objects.create(
        path=path,
        project_id=request.data['project_id'],
        item_type=request.data['item_type'],
        item=request.data['item'],
        inner_order=inner_order,
        attributes=request.data['attributes'],
    )
    return NewNodeSerializer(node_new).data



def update_attributes_node(request, pk):
    """Медод измедения поля attributes"""

    fields_val = [
        'project_id',
        'item_type',
        'item',
        'attributes',
    ]
    validate = Validate(request.data, *fields_val)
    validate.validate_fields_required()

    serializer = NewNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    instance = Node.objects.get(pk=pk)
    instance.attributes = request.data['attributes']
    instance.save()
    return NewNodeSerializer(instance).data






