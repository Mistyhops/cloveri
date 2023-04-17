from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import methods_model


class NodeApiView(APIView):

    # v1/node/<int:pk>/
    def get(self, request, **kwargs):
        """Получить узел по id(pk)"""

        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': 'pk cannot be null'}, status=status.HTTP_400_BAD_REQUEST)

        result = methods_model.get_node(request.GET, pk)
        return Response({'node': result}, status=status.HTTP_200_OK)

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
        return Response({'node': result}, status=status.HTTP_201_CREATED)

    # v1/node/<int:pk>/
    def put(self, request, **kwargs):
        """Изменить поля attributes и inner_order в модели Node"""

        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': 'pk cannot be null'}, status=status.HTTP_400_BAD_REQUEST)

        result = methods_model.change_value_fields(request.data, pk)
        return Response({'node': result}, status=status.HTTP_201_CREATED)

    # v1/node/<int:pk>/
    def delete(self, request, **kwargs):
        """
        Скрыть узел. Установить поле hidden=True
        :param request: в теле запроса принимает следующие параметры:
        project_id: uuid проекта, обязательный параметр
        item_type: обязательный параметр
        item: обязательный параметр
        :return: строку с результатом
        """

        pk = kwargs.get('pk')
        if not pk:
            return Response({'error': 'pk can\'t be None'}, status=status.HTTP_400_BAD_REQUEST)

        result = methods_model.delete_node(request.data, pk)
        return Response({'detail': result}, status=status.HTTP_200_OK)


class NodesApiView(APIView):

    # v1/nodes/
    def get(self, request, **kwargs):
        """Получить потомков узла, если передан id(pk), иначе получить дерево узлов
        по 'project_id' 'item_type' 'item'
        """

        pk = kwargs.get("pk", None)
        if not pk:
            result = methods_model.get_tree(request.GET)
            return Response({'nodes': result}, status=status.HTTP_200_OK)

        result = methods_model.get_children(request.GET, pk)
        return Response({'nodes': result}, status=status.HTTP_200_OK)


class RestoreNodeApiView(APIView):

    # v1/node/<int:pk>/restore/
    def put(self, request, **kwargs):
        """
        Восстановить узел. Установить поле hidden=None
        :param request: в теле запроса принимает следующие параметры:
        project_id: uuid проекта, обязательный параметр
        item_type: обязательный параметр
        item: обязательный параметр
        :return: восстановленный объект
        """

        pk = kwargs.get('pk')
        if not pk:
            return Response({'error': 'pk can\'t be None'}, status=status.HTTP_400_BAD_REQUEST)

        result = methods_model.restore_node(request.data, pk)
        return Response({'node': result}, status=status.HTTP_200_OK)
