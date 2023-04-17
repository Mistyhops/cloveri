from django.db import transaction, DatabaseError
from rest_framework.exceptions import ValidationError, NotFound

from ..models import Node
from ..serializers import NodeSerializer, NewNodeSerializer, UpdateNodeSerializer
from .validate_fields_model import Validate


def get_tree(data: dict) -> dict:
    """Метод вывода всех узлов дерева из модели Node"""

    validate = Validate(data)
    validate.validate_fields_required()

    kwargs = {
        "project_id": data['project_id'],
        "item_type": data['item_type'],
        "item": data['item']
    }
    instance = validate.get_object_from_model(Node, many=True, **kwargs)

    result = NodeSerializer(instance, many=True).data
    return result


def get_node(data: dict, pk: int) -> dict:
    """Метод вывода узла из модели Node"""

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


def create_node(data: dict):
    """Метод создания нового узла в модели Node
    Если в теле запроса передается параметр 'parent_id',
    то будет создан дочерний узел родителя.
    Если в теле запроса отсутствует параметр 'parent_id',
    то будет создан корневой узел.
    """

    fields_allowed = ['parent_id', 'attributes', 'inner_order']
    validate = Validate(data, *fields_allowed)
    validate.validate_fields_required()

    serializer = NewNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    if data.get('parent_id'):
        parent_id = data['parent_id']
        parent = validate.validate_value_fields_for_create_child(parent_id)

        path = parent.path
        path += '0' * (10 - len(str(parent.id))) + str(parent.id)
    else:
        path = ""

    node_new = Node.objects.create(
        path=path,
        project_id=data['project_id'],
        item_type=data['item_type'],
        item=data['item'],
        inner_order=data.get('inner_order'),
        attributes=data.get('attributes'),
    )
    return NewNodeSerializer(node_new).data


def change_value_fields(data: dict, pk: int):
    """Метод изменения значений полей 'attributes' и 'inner_order'
    """
    serializer = UpdateNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    # добавляем в валидатор разрешенные поля
    fields_allowed = ['attributes',]
    kwargs = {'pk': pk}
    validate = Validate(data, *fields_allowed, **kwargs)
    validate.validate_fields_required()

    # получаем 2 объекта. Первый - у которого меняем значения полей
    # Второй объект нужен, чтобы присвоить его полю inner_order значение поля inner_order первого объекта
    instances = validate.validation_change_fields()

    # try:
    #     with transaction.atomic():
    #         if data.get('inner_order'):
    #             instances[0].inner_order, instances[1].inner_order = instances[1].inner_order, instances[0].inner_order
    #             instances[0].save()
    #             instances[1].save()
    # except DatabaseError as e:
    #     raise ValidationError({'error': e})

    if data.get('attributes'):
        instances[0].attributes = data.get('attributes')
        instances[0].save()

    return NewNodeSerializer(instances[0]).data


def delete_node(data: dict, pk: int):
    """Метод скрытия узла, установки параметра hidden=True"""

    validate = Validate(data)
    validate.validate_fields_required()

    serializer = UpdateNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    try:
        with transaction.atomic():
            instance = Node.objects.select_for_update().filter(
                id=pk,
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item'],
            ).exclude(hidden=True).first()

            if not instance:
                raise NotFound('Object not found')

            instance.hidden = True
            instance.save()
    except DatabaseError as e:
        raise ValidationError({'error': e})

    return 'Node deleted'


def restore_node(data: dict, pk: int):
    """Метод скрытия узла, установки параметра hidden=True"""

    validate = Validate(data)
    validate.validate_fields_required()

    serializer = UpdateNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    try:
        with transaction.atomic():
            instance = Node.objects.select_for_update().filter(
                id=pk,
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item'],
                hidden=True,
            ).first()

            if not instance:
                raise NotFound('Object not found')

            instance.hidden = None
            instance.save()
    except DatabaseError as e:
        raise ValidationError({'error': e})

    return NewNodeSerializer(instance).data
