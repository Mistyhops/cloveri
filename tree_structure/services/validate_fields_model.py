from typing import Optional

from rest_framework.exceptions import ValidationError

from ..models import Node


class Validate:
    """Класс для валидации переданных полей при работе с моделью Node"""
    fields_pk = [
        'project_id',
        'item_type',
        'item',
    ]
    def __init__(self, request_data: dict, *args: list|None):
        self.request_data = request_data
        self.fields_pk = __class__.fields_pk
        self.fields_pk += args


    def validate_fields_required(self):
        """Метод проверяет, что в request.data переданы агрументы project_id, item_type, item,
        а также другие необходимые поля"""

        errors = []
        for field in self.fields_pk:
            if field not in self.request_data:
                errors.append(f'{field} field is required.')
        if errors:
            raise ValidationError(errors)


    def validate_children_fields_value(self, parent_id: int):
        """Метод сверяет переданные значения project_id, item_type, item со значениями этих полей у родителя"""

        #если в request_data передан parent_id, значит попытка создать дочерний узел
        if 'parent_id' in self.request_data:
            try:
                instance = Node.objects.get(pk=parent_id)
            except Exception as e:
                raise ValidationError(e)

            errors = []
            if str(instance.project_id) != str(self.request_data['project_id']):
                errors.append(f"Value 'project_id' must match the parent")
            if str(instance.item_type) != str(self.request_data['item_type']):
                errors.append(f"Value 'item_type' must match the parent")
            if str(instance.item) != str(self.request_data['item']):
                errors.append(f"Value 'item' must match the parent")
            if errors:
                raise ValidationError(errors)

            return instance