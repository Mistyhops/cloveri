from django.db import transaction, DatabaseError, connection

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
        test = {'detail': 'Does not exist object(s)'}
        l = []
        l.append(test)
        raise NotFound(l)
        # raise NotFound({'detail': 'Does not exist object(s)'})

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
    try:
        with transaction.atomic():
            amount_nodes = Node.objects.select_for_update().filter(
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

    except DatabaseError as e:
        raise ValidationError({'error': e})

    return node_new


def create_child_node(data: dict, path: str, parent_inner_order: str) -> object:
    try:
        with transaction.atomic():
            amount_nodes = Node.objects.select_for_update().filter(
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
    except DatabaseError as e:
        raise ValidationError({'error': e})

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


def change_inner_order_attr_node(data: dict, pk: int, internal_use: bool = False):
    """    функция смены inner_order    """

    if not pk:
        raise ValidationError({'error': 'pk can\'t be None'})

    fields_allowed = [*data.keys()] if internal_use else ['destination_node_id', ]
    kwargs = {'pk': pk}
    validate = Validate(data, *fields_allowed, **kwargs)
    validate.validate_fields_required()

    serializer = UpdateNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    # проверяем наличие поля destination_node_id, если internal_use = True, то устанавливаем в destination_node_id
    # последний узел
    if not data.get('destination_node_id'):
        if internal_use:
            parent_path = Node.objects.filter(id=pk).first().path[:-10]
            destination_node_id = Node.objects.filter(
                path__startswith=parent_path,
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item']
            ) \
                .annotate(path_len=Length('path')) \
                .exclude(path=parent_path) \
                .filter(path_len__lt=len(parent_path) + 11) \
                .order_by('inner_order') \
                .last().id
            data.update({
                'destination_node_id': destination_node_id
            })
        else:
            raise ValidationError({'error': 'destination_node_id can\'t be None'})

    if pk == int(data.get("destination_node_id")) and not internal_use:
        raise ValidationError({'error': 'must not be equal destination_node_id'})

    try:
        with transaction.atomic():
            # получаем узел, который двигаем
            movable_instance = Node.objects.select_for_update().filter(
                id=pk,
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item']
            ).first()

            if not movable_instance:
                raise NotFound(f'Object with id {pk} not found')

            destination_instance = Node.objects.select_for_update().filter(
                id=data['destination_node_id'],
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item']
            ).first()

            if not destination_instance:
                raise NotFound(f'Object with id {data.get("destination_node_id")} not found')

            if movable_instance.path[:-10] != destination_instance.path[:-10]:
                raise ValidationError(
                    f'Object id {data.get("destination_node_id")} does not belong to the parent of object id {pk}'
                )

            parent_path = destination_instance.path[:-10]

            # если двигаем узел вниз
            if int(movable_instance.inner_order[-10:]) < int(destination_instance.inner_order[-10:]):

                with connection.cursor() as cursor:

                    sql_params = f"""
UPDATE tree_structure_node
    SET inner_order = CASE
        WHEN 
            LENGTH(CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) AS TEXT)) >
            LENGTH(CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) - 1 AS TEXT))
        THEN
            LEFT(inner_order, LENGTH('{destination_instance.inner_order}') - 
            LENGTH(CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) AS TEXT)))||'0'||
            CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) - 1 AS TEXT)||
            RIGHT(inner_order, -LENGTH('{destination_instance.inner_order}'))
        ELSE
            LEFT(inner_order, LENGTH('{destination_instance.inner_order}') - 
            LENGTH(CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10)
            AS INTEGER) - 1 AS TEXT)))||
            CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) - 1 AS TEXT)||
            RIGHT(inner_order, -LENGTH('{destination_instance.inner_order}'))
        END
    WHERE path LIKE '{parent_path}%' 
        AND path != '{parent_path}'
        AND inner_order BETWEEN '{movable_instance.inner_order}' AND '{destination_instance.inner_order}'
        OR inner_order LIKE '{destination_instance.inner_order}%';


UPDATE tree_structure_node
    SET inner_order = '{destination_instance.inner_order}'||RIGHT(inner_order, -LENGTH('{movable_instance.inner_order}'))
    WHERE path LIKE '{movable_instance.path}%'
    RETURNING *;
                    """

                    cursor.execute(sql_params)

                    columns = [col[0] for col in cursor.description]
                    result = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # если двигаем узел вверх
            elif int(movable_instance.inner_order[-10:]) > int(destination_instance.inner_order[-10:]):

                with connection.cursor() as cursor:

                    sql_params = f"""
UPDATE tree_structure_node
    SET inner_order = CASE
        WHEN 
            LENGTH(CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) AS TEXT)) <
            LENGTH(CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) + 1 AS TEXT))
        THEN
            LEFT(inner_order, LENGTH('{destination_instance.inner_order}') - 
            LENGTH(CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) AS TEXT)) - 1)||
            CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) + 1 AS TEXT)||
            RIGHT(inner_order, -LENGTH('{destination_instance.inner_order}'))
        ELSE
            LEFT(inner_order, LENGTH('{destination_instance.inner_order}') - 
            LENGTH(CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) AS TEXT)))||
            CAST(CAST(SUBSTR(inner_order, LENGTH('{destination_instance.inner_order}') - 9, 10) 
            AS INTEGER) + 1 AS TEXT)||
            RIGHT(inner_order, -LENGTH('{destination_instance.inner_order}'))
        END
    WHERE path LIKE '{parent_path}%' 
        AND path != '{parent_path}'
        AND inner_order BETWEEN '{destination_instance.inner_order}' AND '{movable_instance.inner_order}'
        OR inner_order LIKE '{destination_instance.inner_order}%';


UPDATE tree_structure_node
    SET inner_order = '{destination_instance.inner_order}'||
        RIGHT(inner_order, -LENGTH('{movable_instance.inner_order}'))
    WHERE path LIKE '{movable_instance.path}%'
    RETURNING *;
                                        """

                    cursor.execute(sql_params)

                    columns = [col[0] for col in cursor.description]
                    result = [dict(zip(columns, row)) for row in cursor.fetchall()]

            elif not internal_use:
                raise ValidationError({'error': 'movable node\'s inner order is equal to destination node\'s '
                                                'inner order'})
            else:
                return None
    except DatabaseError as e:
        raise ValidationError({'error': e})

    for i in result:
        if i.get('id') == pk:
            return UpdateNodeSerializer(i).data


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
            instance.save(update_fields=['attributes'])
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


def change_parent_node(data: dict, pk: int):
    if not pk:
        raise ValidationError({'error': 'pk can\'t be None'})

    if not data.get('new_parent_id'):
        raise ValidationError({'error': 'new_parent_id is required'})

    fields_allowed = ['new_parent_id', ]
    validate = Validate(data, *fields_allowed)
    validate.validate_fields_required()

    serializer = UpdateNodeSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    try:
        with transaction.atomic():
            movable_instance = Node.objects.select_for_update().filter(
                id=pk,
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item']
            ).first()

            if not movable_instance:
                raise NotFound(f'Object with id {pk} not found')

            # проверяем, что новый родитель не является потомком перемещаемого узла
            descendant_list = Node.objects.filter(
                path__startswith=movable_instance.path
            ) \
                .exclude(path=movable_instance.path) \
                .values_list('id', flat=True)

            if data['new_parent_id'] in descendant_list:
                raise ValidationError({'error': 'New parent can\'t be movable instance\'s descendant'})

            new_parent = Node.objects.select_for_update().filter(
                id=data['new_parent_id'],
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item']
            ).first()

            if not new_parent:
                raise NotFound(f'Object with id {data.get("new_parent_id")} not found')

            new_siblings_quantity = Node.objects.select_for_update().filter(
                path__startswith=new_parent.path,
                project_id=data['project_id'],
                item_type=data['item_type'],
                item=data['item']
            ) \
                .annotate(path_len=Length('path')) \
                .exclude(path=new_parent.path) \
                .filter(path_len__lt=(len(new_parent.path) + 11)) \
                .count()

            new_inner_order = ('0' * (10 - len(str(new_siblings_quantity + 1))) + str(new_siblings_quantity + 1))

            change_inner_order_attr_node(data, pk, internal_use=True)

            with connection.cursor() as cursor:
                sql_params = f"""
UPDATE tree_structure_node
    SET path = '{new_parent.path}'||RIGHT(path, -LENGTH('{movable_instance.path[:-10]}')),
        inner_order = '{new_parent.inner_order}'||'{new_inner_order}'
        ||RIGHT(inner_order, -LENGTH('{movable_instance.inner_order}'))
    WHERE path LIKE '{movable_instance.path}%'
    RETURNING *;
                """
                cursor.execute(sql_params)

                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except DatabaseError as e:
        raise ValidationError({'error': e})

    for i in result:
        if i.get('id') == pk:
            return UpdateNodeSerializer(i).data
