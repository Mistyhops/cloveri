import json
import uuid
from django.db import models
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
        """Метод проверяет, что в request.data переданы аргументы project_id, item_type, item,
        а также другие необходимые поля
        """

        errors = []

        # Проверяем, переданы ли обязательные аргументы
        for field in self.fields_pk:
            if field not in self.request_data:
                errors.append(f'{field} field is required.')

        # Проверяем, не переданы ли лишние аргументы
        for attr in self.request_data:
            if attr not in self.fields_allowed:
                errors.append(f'{attr} not allowed')

        # Проверка форматов переданных полей
        errors += self._validate_fields_format()

        if errors:
            raise ValidationError({'errors': errors})

    def validate_value_fields_for_create_child(self, parent_id: int) -> object:
        """
        Метод сверяет переданные значения project_id, item_type, item со значениями этих полей у родителя,
        Формирует inner_order и возвращает его, а также возвращает path родителя
        """

        kwargs = {"pk": parent_id}
        instance = self.get_object_from_model(Node, many=False, **kwargs)

        errors = []
        if str(instance.project_id) != str(self.request_data['project_id']):
            errors.append(f"Value 'project_id' must match the parent")
        if str(instance.item_type) != str(self.request_data['item_type']):
            errors.append(f"Value 'item_type' must match the parent")
        if str(instance.item) != str(self.request_data['item']):
            errors.append(f"Value 'item' must match the parent")
        if len(instance.path) % 10 != 0:
            errors.append({'error': f'For object id {instance.id} value field "path" not a multiple of 10. '
                                    f'Field "path" generation error.'})
        if errors:
            raise ValidationError(errors)

        return instance

    def get_object_from_model(self, model: models.Model, many: bool = False, **kwargs) -> object:
        if many:
            instance = model.objects.filter(**kwargs).exclude(hidden=True)
        else:
            instance = model.objects.filter(**kwargs).exclude(hidden=True).first()

        if not instance:
            raise NotFound({'detail': 'Does not exist object(s)'})

        return instance

    def _validate_fields_format(self):
        errors = []

        # Проверка форматов переданных полей
        project_id = self.request_data.get('project_id')
        if project_id and not isinstance(project_id, uuid.UUID):
            try:
                uuid.UUID(project_id)
            except (AttributeError, ValueError) as e:
                errors.append('project_id has wrong format, must be uuid')

        item_type = self.request_data.get('item_type')
        if item_type and not isinstance(item_type, str):
            errors.append('item_type has wrong format, must be str')

        item = self.request_data.get('item')
        if item and not isinstance(item, str):
            errors.append('item has wrong format, must be str')

        parent_id = self.request_data.get('parent_id')
        if parent_id and not isinstance(parent_id, int):
            errors.append('parent_id has wrong format, must be int')


        inner_order = self.request_data.get('inner_order')
        if inner_order and not isinstance(inner_order, str):
            errors.append('inner_order has wrong format, must be str')

        attributes = self.request_data.get('attributes')
        if attributes:
            if isinstance(attributes, str):
                try:
                    attr_dict = json.loads(attributes)
                    if not isinstance(attr_dict, dict):
                        errors.append('attributes has wrong format, must be json')
                except json.decoder.JSONDecodeError:
                    errors.append('attributes has wrong format, must be json')
            else:
                errors.append('attributes has wrong format, must be json')

        hidden = self.request_data.get('hidden')
        if hidden is not None and hidden is not True:
            errors.append('hidden can be None or True')

        destination_node_id = self.request_data.get('destination_node_id')
        if destination_node_id and not isinstance(destination_node_id, int):
            errors.append('destination_node_id has wrong format, must be int')

        new_parent_id = self.request_data.get('new_parent_id')
        if new_parent_id and not isinstance(new_parent_id, int):
            errors.append('new_parent_id has wrong format, must be int')

        return errors
