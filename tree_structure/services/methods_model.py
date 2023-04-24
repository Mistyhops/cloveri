from django.db import transaction, DatabaseError
from django.db.models.functions import Length
from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import F

from ..models import Node
from ..serializers import NodeSerializer, NewNodeSerializer, UpdateNodeSerializer, DeleteNodeSerializer
from .validate_fields_model import Validate


def get_tree(data: dict) -> dict:
    """Метод вывода всех узлов дерева из модели Node"""

    validate = Validate(data)
    validate.validate_fields_required()

    instance = Node.objects.filter(
        project_id=data['project_id'],
        item_type=data['item_type'],
        item=data['item'],
    ).exclude(hidden=True).order_by('path')

    if not instance:
        raise NotFound({'error': 'does not exist object(s)'})

    result = NodeSerializer(instance, many=True).data
    return result


def get_node(data: dict, pk: int) -> dict:
    """Метод вывода узла из модели Node"""

    if not pk:
        raise ValidationError({'error': 'pk can\'t be None'})

    validate = Validate(data)
    validate.validate_fields_required()

    kwargs = {
        "pk": pk,
        "project_id": data['project_id'],
        "item_type": data['item_type'],
        "item": data['item']
    }
    instance = validate.get_object_from_model(Node, many=False, **kwargs)

    serializer = NodeSerializer(instance, many=False).data
    return serializer


def get_children(data: dict, pk: int) -> dict:
    """Метод вывода всех дочерних узлов из модели Node"""

    if not pk:
        raise ValidationError({'error': 'pk can\'t be None'})

    validate = Validate(data)
    validate.validate_fields_required()

    kwargs = {"pk": pk}
    instance = validate.get_object_from_model(Node, many=False, **kwargs)

    # получаем path родителя
    path = instance.path
    # формируем path дочерних узлов
    path += '0' * (10 - len(str(instance.id))) + str(instance.id)

    kwargs = {
        "path__startswith": path,
        "project_id": data['project_id'],
        "item_type": data['item_type'],
        "item": data['item']
    }
    instance = validate.get_object_from_model(Node, many=True, **kwargs)

    result = NodeSerializer(instance, many=True).data
    return result


def create_root_node(data: dict, path: str) -> object:
    amount_nodes = Node.objects.filter(
        project_id=data['project_id'],
        item_type=data['item_type'],
        item=data['item'],
    ).annotate(path_len=Length('path')).filter(path_len__lt=11).count()

    inner_order = amount_nodes + 1

    node_new = Node.objects.create(
        path=path,
        project_id=data['project_id'],
        item_type=data['item_type'],
        item=data['item'],
        inner_order=inner_order,
        attributes=data.get('attributes'),
    )
    path = '0' * (10 - len(str(node_new.id))) + str(node_new.id)
    node_new.path = path
    node_new.save()
    return node_new


def create_child_node(data: dict, path: str) -> object:
    amount_nodes = Node.objects.filter(
        path__startswith=path,
        project_id=data['project_id'],
        item_type=data['item_type'],
        item=data['item'],
    ).exclude(path=path).count()

    inner_order = amount_nodes + 1

    node_new = Node.objects.create(
        path=path,
        project_id=data['project_id'],
        item_type=data['item_type'],
        item=data['item'],
        inner_order=inner_order,
        attributes=data.get('attributes'),
    )
    path = '0' * (10 - len(str(node_new.id))) + str(node_new.id)
    node_new.path += path
    node_new.save()
    return node_new


def create_node(data: dict):
    """Метод создания нового узла в модели Node
    Если в теле запроса передается параметр 'parent_id',
    то будет создан дочерний узел родителя.
    Если в теле запроса отсутствует параметр 'parent_id',
    то будет создан корневой узел.
    """

    fields_allowed = ['parent_id', 'attributes']
    validate = Validate(data, *fields_allowed)
    validate.validate_fields_required()

    serializer = NewNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    if data.get('parent_id'):
        parent_id = data['parent_id']
        instance_parent = validate.validate_value_fields_for_create_child(parent_id)
        node_new = create_child_node(data, instance_parent.path)
    else:
        node_new = create_root_node(data, "9999999999")

    return NewNodeSerializer(node_new).data


def change_inner_order_attr_node(data: dict, pk: int):
    pass
    # if not pk:
    #     raise ValidationError({'error': 'pk can\'t be None'})
    #
    # if not data.get('node_id'):
    #     raise ValidationError({'error': 'node_id param is required.'})
    #
    # fields_allowed = ['node_id', ]
    # kwargs = {'pk': pk}
    # validate = Validate(data, *fields_allowed, **kwargs)
    # validate.validate_fields_required()
    #
    # serializer = UpdateNodeSerializer(data=data)
    # serializer.is_valid(raise_exception=True)
    #
    # try:
    #     with transaction.atomic():
    #         instance = Node.objects.select_for_update().filter(
    #             id=pk,
    #             project_id=data['project_id'],
    #             item_type=data['item_type'],
    #             item=data['item']
    #         ).first()
    #
    #         if not instance:
    #             raise NotFound('Object not found')
    #
    #         instance.attributes = data.get('attributes')
    #         instance.save()
    # except DatabaseError as e:
    #     raise ValidationError({'error': e})

    #
    # a.update(inner_order=F("inner_order") + 1)
    #
    # Node.objects.filter(path__startswith='00000000010', inner_order__gte=3000, inner_order__lte=7000).values('id',
    #                                                                                                          'path',
    #                                                                                                          'inner_order')


def change_attributes_attr_node(data: dict, pk: int):
    """    Функция изменения значения поля attributes в модели Node    """

    if not pk:
        raise ValidationError({'error': 'pk can\'t be None'})

    if not data.get('attributes'):
        raise ValidationError({'error': 'attributes param is required.'})

    fields_allowed = ['attributes', ]
    kwargs = {'pk': pk}
    validate = Validate(data, *fields_allowed, **kwargs)
    validate.validate_fields_required()

    serializer = UpdateNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    try:
        with transaction.atomic():
            instance = Node.objects.select_for_update().filter(
                id=pk,
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item']
            ).first()

            if not instance:
                raise NotFound('Object not found')

            instance.attributes = data.get('attributes')
            instance.save()
    except DatabaseError as e:
        raise ValidationError({'error': e})


def change_hidden_attr_node(data: dict, pk: int):
    if not pk:
        raise ValidationError({'error': 'pk can\'t be None'})

    try:
        hidden = data['hidden']
    except KeyError:
        raise ValidationError({'error': 'hidden field is required'})

    fields_allowed = ['hidden', ]
    validate = Validate(data, *fields_allowed)
    validate.validate_fields_required()

    serializer = DeleteNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    try:
        with transaction.atomic():
            instance = Node.objects.select_for_update().filter(
                id=pk,
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item']
            ).first()

            if not instance:
                raise NotFound('Object not found')

            if instance.hidden == hidden:
                raise ValidationError({'error': f'hidden is already set to {instance.hidden}'})
            else:
                instance.hidden = hidden
                instance.save()
    except DatabaseError as e:
        raise ValidationError({'error': e})

    if hidden:
        return 'Node deleted'
    else:
        return NewNodeSerializer(instance).data
