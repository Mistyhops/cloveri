from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import methods_model


class GetNodeApiView(APIView):

    # v1/node/<int:pk>/
    def get(self, request, **kwargs):
        """Получить узел по id(pk)"""

        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': 'pk cannot be null'}, status=status.HTTP_404_NOT_FOUND)

        result = methods_model.get_node(request.data, pk)
        return Response({'node': result}, status=status.HTTP_200_OK)

    # v1/node/<int:pk>/
    def put(self, request, **kwargs):
        """Изменить поля attributes и inner_order в моделе Node"""

        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': 'pk cannot be null'})

        result = methods_model.change_value_fields(request.data, pk)
        return Response({'node': result}, status=status.HTTP_201_CREATED)

    def delete(self):
        """Скрыть узел. Установить поле hidden=True"""
        pass


class GetNodesApiView(APIView):

    # v1/nodes/
    def get(self, request, **kwargs):
        """Получить потомков узла, если передан id, иначе получить все корневые узлы"""
        pk = kwargs.get("pk", None)
        if not pk:
            result = methods_model.get_tree(request.data)
            return Response({'nodes': result}, status=status.HTTP_200_OK)

        result = methods_model.get_children(request.data, pk)
        return Response({'nodes': result}, status=status.HTTP_200_OK)


class CreateNodeApiView(APIView):

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

        try:
            result = methods_model.create_node(request.data)
            return Response({'node': result}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)
