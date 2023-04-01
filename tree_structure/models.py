
from django.db import models


class Node(models.Model):
    # id = models.BigAutoField(primary_key=True)
    path = models.TextField()
    project_id = models.UUIDField()
    item_type = models.TextField()
    item = models.TextField()
    inner_order = models.BigIntegerField()
    attributes = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tree_structure_node'
        unique_together = (('path', 'id'), ('id', 'project_id', 'item_type', 'item'),)

    # def __str__(self):
    #     return f'{self.item}: {self.id}, {self.path}'
    #

