
from ..models import Node
from ..serializers import NewNodeSerializer, NodeSerializer
from rest_framework.generics import get_object_or_404

def get_all_node():
    """Метод вывода всех записей из модели Node"""
    result = NodeSerializer(Node.objects.all(), many=True).data
    return result


def create_node(request):
    """Метод создания нового узла в модели Node"""
    serializer = NewNodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    #здесь остается вопрос, как валидировать project_id, если parent_id не передаем
    #и создаем корневой узел. Теоритически project_id не должен продублироваться

    try:
        parent_id = request.data['parent_id']
        parent = get_object_or_404(Node, id=parent_id)
        new_node_path = '0' * (10 - len(str(parent.id))) + str(parent.id)
        path = parent.path + new_node_path

        num_child = Node.objects.filter(path=path)
        inner_order = len(num_child) + 1
    except KeyError:
        obj = Node.objects.latest('id')
        new_id_path = obj.id + 1
        path = '0' * (10 - len(str(new_id_path))) + str(new_id_path)
        inner_order = 1


    node_new = Node.objects.create(
        path=path,
        project_id=request.data['project_id'],
        item_type=request.data['item_type'],
        item=request.data['item'],
        inner_order=inner_order,
        attributes=request.data['attributes'],
    )
    return NewNodeSerializer(node_new).data

