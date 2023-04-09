from typing import Optional

from rest_framework.exceptions import ValidationError, NotFound

from ..models import Node


class Validate:
    """Класс для валидации переданных полей при работе с моделью Node"""
    fields_pk = (
        'project_id',
        'item_type',
        'item',
    )

    def __init__(self, request_data: dict, *args, **kwargs):
        self.request_data = request_data
        self.fields_pk = Validate.fields_pk
        self.fields_allowed = Validate.fields_pk
        self.fields_allowed += args
        self.pk = kwargs.get('pk')

    def validate_fields_required(self):
        """Метод проверяет, что в request.data переданы агрументы project_id, item_type, item,
        а также другие необходимые поля"""

        errors = []

        # Проверяем, переданы ли обязательные аргументы
        for field in self.fields_pk:
            if field not in self.request_data:
                errors.append(f'{field} field is required.')

        # Проверяем, не переданы ли лишние аргументы
        for attr in self.request_data:
            if attr not in self.fields_allowed:
                errors.append(f'{attr} not allowed')

        if errors:
            raise ValidationError(errors)

    def validate_value_fields_for_create_child(self, parent_id: int) -> object:
        """Метод сверяет переданные значения project_id, item_type, item со значениями этих полей у родителя"""

        # если в request_data передан parent_id, значит попытка создать дочерний узел
        if 'parent_id' in self.request_data:
            kwargs = {"pk": parent_id}
            instance = self.get_object_from_model(Node, many=False, **kwargs)

            errors = []
            if str(instance.project_id) != str(self.request_data['project_id']):
                errors.append(f"Value 'project_id' must match the parent")
            if str(instance.item_type) != str(self.request_data['item_type']):
                errors.append(f"Value 'item_type' must match the parent")
            if str(instance.item) != str(self.request_data['item']):
                errors.append(f"Value 'item' must match the parent")
            if errors:
                raise ValidationError({'errors': errors})

            return instance

    def validation_change_fields(self) -> list:
        """Метод проверяет парамерты для смены inner_order или изменение поля attributes.
        Учитываем, что запрос на изменение может быть для двух полей одновременно
        или для какого-то одного поля.
        """

        # будет содержать узел, с последним по счету inner_order
        instance_original_inner_order = None

        # Получаем узел, поля которого будем менять (inner_order, attributes)
        kwargs = {
            "pk": self.pk,
            "project_id": self.request_data['project_id'],
            "item_type": self.request_data['item_type'],
            "item": self.request_data['item']
        }
        instance_change = self.get_object_from_model(Node, many=False, **kwargs)

        #Если в запрос был передан парамерт inner_order, то ищем узел с таким inner_order
        if self.request_data.get('inner_order'):
            path = instance_change.path

            kwargs = {
                "path__startswith": path,
                "project_id": self.request_data['project_id'],
                "item_type": self.request_data['item_type'],
                "item": self.request_data['item'],
                "inner_order": self.request_data.get('inner_order')
            }
            instance_original_inner_order = self.get_object_from_model(Node, many=False, **kwargs)

        return instance_change, instance_original_inner_order

    def get_object_from_model(self, model: object, many: bool = False, **kwargs) -> object:
        model = model

        if many:
            instance = model.objects.filter(**kwargs).exclude(hidden=True)
        else:
            instance = model.objects.filter(**kwargs).exclude(hidden=True).first()

        if not instance:
            raise NotFound({'error': 'does not exist object(s)'})

        return instance


