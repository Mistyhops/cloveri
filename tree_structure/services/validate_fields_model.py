from rest_framework.exceptions import ValidationError

from ..models import Node


class Validate:
    """Класс для валидации переданных полей при работе с моделью Node"""
    def __init__(self, request_data, *args):
        self.request_data = request_data
        self.fields = args

    def validate_fields_required(self):
        """Метод проверяет, что переданный в self.fields список полей имеется в self.request_data"""
        errors = []
        for field in self.fields:
            if field not in self.request_data:
                errors.append(f'{field} field is required.')
        if errors:
            raise ValidationError(errors)

    def validate_parent_id_value(self, parent_id):
        """Метод сверяет переданные значение полей с родительскими"""

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