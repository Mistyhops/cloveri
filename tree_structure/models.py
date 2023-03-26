# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Node(models.Model):
    id = models.BigAutoField(primary_key=True)
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

    def __str__(self):
        return f'{self.item}: {self.id}, {self.path}'

    @classmethod
    def get_tree(cls, item=None):
        if item:
            return cls.objects.filter(item=item)
        return cls.objects.all()

    @classmethod
    def add_root(cls, project_id: str, item_type: str, item: str, inner_order: int = 1,
                 attributes: str = None):
        """
        Adds root node to the tree

        :param project_id: project_id for root node is required, project_id must be UUID
        :param item_type: item_type for root node is required
        :param item: item for root node is required
        :param inner_order: order of the nodes with one parent, default is 1
        :param attributes: node attrs in json, default is None
        :return: new node
        """
        new_node = cls(
            path='',
            project_id=project_id,
            item_type=item_type,
            item=item,
            inner_order=inner_order,
            attributes=attributes
        )
        new_node.save()

        return new_node

    def add_child(self, inner_order: str = 1, attributes: str = None, **kwargs):
        """
        Adds a child to the node.

        :param inner_order: order of the nodes with one parent, default is 1
        :param attributes: node attrs in json, default is None
        :param kwargs: project_id, item_type and item child node inherits from current(parent) node
        :return: new node
        """
        new_node_path = '0' * (10 - len(str(self.id))) + str(self.id)
        path = self.path + new_node_path

        project_id = self.project_id
        item_type = self.item_type
        item = self.item

        new_node = Node(
            path=path,
            project_id=project_id,
            item_type=item_type,
            item=item,
            inner_order=inner_order,
            attributes=attributes
        )
        new_node.save()

        return new_node
