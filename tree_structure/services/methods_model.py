from django.db import transaction, DatabaseError
from django.db.models import F
from django.db.models.functions import Length
from rest_framework.exceptions import ValidationError, NotFound

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
    ).exclude(hidden=True).order_by('inner_order')

    if not instance:
        raise NotFound({'detail': 'Does not exist object(s)'})

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
        "path__startswith": path[:-10],
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

    inner_order = '0' * (10 - len(str(amount_nodes + 1))) + str(amount_nodes + 1)

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


def create_child_node(data: dict, path: str, parent_inner_order: str) -> object:
    amount_nodes = Node.objects.filter(
        path__startswith=path,
        project_id=data['project_id'],
        item_type=data['item_type'],
        item=data['item'],
    ) \
        .annotate(path_len=Length('path')) \
        .exclude(path=path) \
        .filter(path_len__lt=len(path) + 11) \
        .count()

    inner_order = parent_inner_order + ('0' * (10 - len(str(amount_nodes + 1))) + str(amount_nodes + 1))

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

        node_new = create_child_node(data, instance_parent.path, instance_parent.inner_order)
    else:
        node_new = create_root_node(data, "9999999999")

    return NewNodeSerializer(node_new).data


def change_inner_order_attr_node(data: dict, pk: int):
    """    функция смены inner_order    """

    if not pk:
        raise ValidationError({'error': 'pk can\'t be None'})

    fields_allowed = ['destination_node_id', ]
    kwargs = {'pk': pk}
    validate = Validate(data, *fields_allowed, **kwargs)
    validate.validate_fields_required()

    serializer = UpdateNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    if pk == int(data.get("destination_node_id")):
        raise ValidationError({'error': 'must not be equal destination_node_id'})

    """
    try:
        with transaction.atomic():
            # получаем узел который двигаем
            kwargs = {
                "pk": pk,
                "project_id": data['project_id'],
                "item_type": data['item_type'],
                "item": data['item']
            }
            movable_instance = validate.get_object_from_model(Node, many=False, **kwargs)

            # получаем узел который двигаем и его детей
            movable_instances = Node.objects.select_for_update().filter(
                inner_order__startswith=movable_instance.inner_order,
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item']
            ).order_by("inner_order")[1:]

            # узел, на место которого двигаем узел movable_instance
            # берем его без блокировки, чтобы узлань его inner_order
            destination_instance = Node.objects.select_for_update().filter(
                id=data.get('destination_node_id'),
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item']
            ).first()

            if not movable_instance:
                raise NotFound(f'Object with id{pk} not found')

            if not destination_instance:
                raise NotFound(f'Object with id{data.get("destination_node_id")} not found')

            if movable_instance.path[:-10] != destination_instance.path[:-10]:
                raise ValidationError(
                    f'Object id{data.get("destination_node_id")} does not belong to the parent of object id{pk}')

            # пересчитываем inner_order для узла и его детей, которые двигаем
            movable_instance.inner_order = destination_instance.inner_order
            movable_instance.save()
            movable_instances.update(inner_order=movable_instance.inner_order + F("inner_order")[len(movable_instance.inner_order):])
            movable_instances.save()

            # print('1    ==============================            =======================         ===============')

            # [-10:] берем 10 последних символов и преобразуем в int чтобы убрать лишние нули
            # если двигаем узел наверх
            if int(movable_instance.inner_order[-10:]) > int(destination_instance.inner_order[-10:]):
                other_instance = Node.objects.select_for_update().filter(
                    inner_order__startswith=movable_instances[0].inner_order[:-10],
                    project_id=data['project_id'],
                    item_type=data['item_type'],
                    item=data['item']
                ).exclude(id=movable_instances[0].id).order_by('inner_order')[1:]


                # for item in instance_all:
                #     item.inner_order = _inner_order[-10:] + ('0' * (10 - len(str(_inner_order[-10:]))) + str(node_new.id))
                # instance_all.save()
                #
                # instance_new.inner_order = _inner_order
                # instance_new.save()

                # instance_all.update(inner_order=int(F("inner_order")[-10:]) + 1)


    except DatabaseError as e:
        raise ValidationError({'error': e})

    # a.update(inner_order=F("inner_order") + 1)
    #
    # Node.objects.filter(path__startswith='00000000010', inner_order__gte=3000, inner_order__lte=7000).values('id',
    #                                                                                                          'path',
    #                                                                                                          'inner_order')
    # return UpdateNodeSerializer(instance_new).data"""


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

    return UpdateNodeSerializer(instance).data


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
