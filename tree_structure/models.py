from django.db import models


class Node(models.Model):
    id = models.BigAutoField(primary_key=True)
    path = models.TextField()
    project_id = models.UUIDField()
    item_type = models.TextField()
    item = models.TextField()
    inner_order = models.BigIntegerField()
    attributes = models.JSONField(blank=True, null=True)
    hidden = models.BooleanField(blank=True, null=True)

    def get_level_node(self):
        if len(self.path) < 10:
            return 0
        elif len(self.path) == 10:
            return 1
        elif len(self.path) > 10:
            return len(self.path) // 10

    class Meta:
        db_table = 'tree_structure_node'
        unique_together = (('path', 'id'), ('id', 'project_id', 'item_type', 'item'),)
