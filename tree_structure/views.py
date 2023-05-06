from operator import itemgetter

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import methods_model


class NodeApiView(APIView):

    # v1/node/<int:pk>/
    def get(self, request, **kwargs):
        """
        Получить узел по id(pk)
        :param request: в параметрах get запроса принимает следующие параметры:
        project_id: uuid проекта, обязательный параметр
        item_type: обязательный параметр
        item: обязательный параметр
        :return: объект
        """

        result = methods_model.get_node(request.GET, kwargs.get("pk", None))
        return Response(result, status=status.HTTP_200_OK)

    # v1/node/
    def post(self, request):
        """
        Создание нового узла. Запрос post.
        :param request: в теле запроса принимает следующие параметры:
        parent_id (optional): id родителя, передается при создании дочернего (некорневого) узла
        project_id: uuid проекта, обязательный параметр, при создании дочернего узла сверяется с соответствующим
        полем (project_id) родителя, при несоответствии возвращает ответ 400
        item_type: обязательный параметр, при создании дочернего узла сверяется с соответствующим полем (item_type)
        родителя, при несоответствии возвращает ответ 400
        item: обязательный параметр, при создании дочернего узла сверяется с соответствующим полем (item) родителя,
        при несоответствии возвращает ответ 400
        :return: при успешном выполнении запроса возвращает созданный объект, в ином случае - ошибку
        """

        result = methods_model.create_node(request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class NodesApiView(APIView):

    # v1/nodes/
    def get(self, request, **kwargs):
        """
        Получить потомков узла, если в url передан id(pk), иначе получить дерево узлов
        по 'project_id' 'item_type' 'item'
        :param request: в параметрах get запроса принимает следующие параметры:
        project_id: uuid проекта, обязательный параметр
        item_type: обязательный параметр
        item: обязательный параметр
        :return: список объектов
        """

        pk = kwargs.get("pk", None)
        if not pk:
            result = methods_model.get_tree(request.GET)

            # print(ss, 'sdfsdfsdfsdfsdfs')
            # sorted(result, key=lambda x: x[2])
            # ss = sorted(result, key=itemgetter('test'))
            return Response(result, status=status.HTTP_200_OK)

        result = methods_model.get_children(request.GET, pk)
        return Response(result, status=status.HTTP_200_OK)


class ChangeAttributesNodeApiView(APIView):
    # v1/node/<int:pk>/
    def put(self, request, **kwargs):
        """
        Изменить поле attributes в модели Node
        :param request:
         - В параметрах put запроса в url принимает pk.
         - В парамертах тела запроса:
        project_id: uuid проекта, обязательный параметр
        item_type: обязательный параметр
        item: обязательный параметр
        attributes: json
        :return: объект
        """

        result = methods_model.change_attributes_attr_node(request.data, kwargs.get("pk", None))
        return Response(result, status=status.HTTP_201_CREATED)


class ChangeInnerOrderNodeApiView(APIView):

    # v1/node/<int:pk>/order
    def put(self, request, **kwargs):
        """
        Изменить поле inner_order в модели Node
        :param request:
         - В параметрах put запроса в url принимает pk.
         - В парамертах тела запроса:
        project_id: uuid проекта, обязательный параметр
        item_type: обязательный параметр
        item: обязательный параметр
        destination_node_id: id узла, на место которого ставим
        :return: сообщение
        """
        result = methods_model.change_inner_order_attr_node(request.data, kwargs.get("pk"), kwargs.get("destination_node_id"))
        return Response(result, status=status.HTTP_201_CREATED)


class DeleteRestoreNodeApiView(APIView):

    # v1/node/<int:pk>/hidden/
    def put(self, request, **kwargs):
        """
        Скрыть или восстановить узел (установить поле hidden)
        :param request: в теле запроса принимает следующие параметры:
        project_id: uuid проекта, обязательный параметр
        item_type: обязательный параметр
        item: обязательный параметр
        hidden: обязательный параметр, принимает возможные значения True или None (для удаления необходимо передать
        True, для восстановления - None)
        :return: при восстановлении - восстановленный объект, при удалении - строка с результатом
        """

        result = methods_model.change_hidden_attr_node(request.data, kwargs.get('pk'))
        return Response(result, status=status.HTTP_200_OK)
