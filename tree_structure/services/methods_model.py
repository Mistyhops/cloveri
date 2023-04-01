
from ..models import Node
from ..serializers import NewNodeSerializer, NodeSerializer
from rest_framework.generics import get_object_or_404

def get_all_node():
    result = NodeSerializer(Node.objects.all(), many=True).data
    return result


def create_node(request):
    serializer = NewNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    parent_id = request.data['parent_id']

    if not parent_id:
        node_new = Node.objects.create(
            project_id=request.data['project_id'],
            item_type=request.data['item_type'],
            item=request.data['item'],
            inner_order=request.data['inner_order'],
            attributes=request.data['attributes'],
        )

    else:
        parent = get_object_or_404(Node, id=parent_id)
        print(parent.path)
        new_node_path = '0' * (10 - len(str(parent.path))) + str(parent_id)
        path = parent.path + new_node_path
        node_new = Node.objects.create(
            path=path,
            project_id=request.data['project_id'],
            item_type=request.data['item_type'],
            item=request.data['item'],
            inner_order=request.data['inner_order'],
            attributes=request.data['attributes'],
        )
    return NewNodeSerializer(node_new).data





# @classmethod
    # def add_root(cls, project_id: str, item_type: str, item: str, inner_order: int = 1,
    #              attributes: str = None):
    #     """
    #     Adds root node to the tree
    #
    #     :param project_id: project_id for root node is required, project_id must be UUID
    #     :param item_type: item_type for root node is required
    #     :param item: item for root node is required
    #     :param inner_order: order of the nodes with one parent, default is 1
    #     :param attributes: node attrs in json, default is None
    #     :return: new node
    #     """
    #
    #     item_type = item_type.strip()
    #     item = item.strip()
    #
    #     new_node = cls(
    #         path='',
    #         project_id=project_id,
    #         item_type=item_type,
    #         item=item,
    #         inner_order=inner_order,
    #         attributes=attributes
    #     )
    #     new_node.save()
    #
    #     return new_node
    #
    # def add_child(self, project_id: str, item_type: str, item: str, inner_order: str = 1,
    #               attributes: str = None, **kwargs):
    #     """
    #     Adds a child to the node.
    #
    #     :param project_id: project_id must be UUID. project_id for child note is required, and it must be equal
    #     to parent's project_id, if not raise ValueError
    #     :param item_type: item_type for child note is required, and it must be equal to parent's item_type,
    #     if not raise ValueError
    #     :param item: item for child note is required, and it must be equal to parent's item,
    #     if not raise ValueError
    #     :param inner_order: order of the nodes with one parent, default is 1
    #     :param attributes: node attrs in json, default is None
    #     :param kwargs: project_id, item_type and item child node inherits from current(parent) node
    #     :return: new node
    #     """
    #     new_node_path = '0' * (10 - len(str(self.id))) + str(self.id)
    #     path = self.path + new_node_path
    #
    #     item_type = item_type.strip()
    #     item = item.strip()
    #
    #     if not project_id == self.project_id:
    #         raise ValueError('child note\'s project_id must be equal ot parent\'s project_id')
    #     if not item_type.lower() == self.item_type.strip().lower():
    #         raise ValueError('child note\'s item_type must be equal ot parent\'s item_type')
    #     if not item.lower() == self.item.strip().lower():
    #         raise ValueError('child note\'s item must be equal ot parent\'s item')
    #
    #     new_node = Node(
    #         path=path,
    #         project_id=project_id,
    #         item_type=item_type,
    #         item=item,
    #         inner_order=inner_order,
    #         attributes=attributes
    #     )
    #     new_node.save()
    #
    #     return new_node