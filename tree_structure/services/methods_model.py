from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from ..models import Node
from ..serializers import NodeSerializer, NewNodeSerializer

from .validate_fields_model import Validate


# def fields(*fields_val):
#     def decorator_validate_fields(func):
#         def wrap(data):
#             validate = Validate(data, fields_val)
#             validate.validate_fields_required()
#         return wrap
#     return decorator_validate_fields


def get_tree(data: dict):
    """Метод вывода всех корневых узлов из модели Node"""

    validate = Validate(data)
    validate.validate_fields_required()

    instance = Node.objects.filter(
        project_id=data['project_id'],
        item_type=data['item_type'],
        item=data['item'],
        path="")

    result = NodeSerializer(instance, many=True).data
    return result


def get_node(data: dict, pk: int):
    """Метод вывода узла из модели Node"""

    validate = Validate(data)
    validate.validate_fields_required()

    instance = get_object_or_404(Node,
                                 pk=pk,
                                 project_id=data['project_id'],
                                 item_type=data['item_type'],
                                 item=data['item']
                                 )
    serializer = NodeSerializer(instance, many=False).data
    return serializer


def get_children(data: dict, pk: int):
    """Метод вывода всех дочерних узлов из модели Node"""
    instance = get_object_or_404(Node, pk=pk)
    path = instance.path
    path += '0' * (10 - len(str(instance.id))) + str(instance.id)


    validate = Validate(data)
    validate.validate_fields_required()

    queryset = Node.objects.filter(
        path__startswith=path,
        project_id=data['project_id'],
        item_type=data['item_type'],
        item=data['item'])
    result = NodeSerializer(queryset, many=True).data
    return result


# fields_val=['project_id', 'item_type', 'item']
# @fields(fields_val)
def create_node(data):
    """Метод создания нового узла в модели Node"""

    validate = Validate(data)
    validate.validate_fields_required()

    serializer = NewNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    try:
        parent_id = data['parent_id']
        parent = validate.validate_children_fields_value(parent_id)
        path = parent.path
        path += '0' * (10 - len(str(parent.id))) + str(parent.id)
        num_child = Node.objects.filter(path=path)
        inner_order = len(num_child) + 1
    except KeyError:
        path = ""
        inner_order = 1


    node_new = Node.objects.create(
        path=path,
        project_id=data['project_id'],
        item_type=data['item_type'],
        item=data['item'],
        inner_order=inner_order,
        attributes=data.get('attributes'),
    )
    return NewNodeSerializer(node_new).data



def update_attributes_node(data, pk):
    """Медод измедения поля attributes"""

    fields = ['attributes',]
    validate = Validate(data, *fields)
    validate.validate_fields_required()

    serializer = NewNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    instance = get_object_or_404(Node,
                                 pk=pk,
                                 project_id=data['project_id'],
                                 item_type=data['item_type'],
                                 item=data['item']
                                 )

    instance.attributes = data['attributes']
    instance.save()
    return NewNodeSerializer(instance).data





