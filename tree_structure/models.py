from django.db import models

from rest_framework.exceptions import ValidationError


class Node(models.Model):
    id = models.BigAutoField(primary_key=True)
    path = models.TextField()
    project_id = models.UUIDField()
    item_type = models.TextField()
    item = models.TextField()
    inner_order = models.TextField()
    attributes = models.JSONField(blank=True, null=True)
    hidden = models.BooleanField(blank=True, null=True)

    def get_level_node(self):
        if len(self.path) % 10 == 0:
            return len(self.path) // 10
        else:
            raise ValidationError(f"For object id {self.id} value field 'path' not a multiple of 10. "
                                  f"Field 'path' generation error.")

    class Meta:
        db_table = 'tree_structure_node'
        unique_together = (('path', 'id'), ('id', 'project_id', 'item_type', 'item'),)
