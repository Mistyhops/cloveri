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
        """Изменить поле attributes по id(pk)"""

        # pk = kwargs.get("pk", None)
        # if not pk:
        #     return Response({'error': 'pk cannot be null'})
        #
        # result = methods_model.update_value_fields(request.data, pk)
        # return Response({'node': result}, status=status.HTTP_201_CREATED)
        return Response({'node': 'method is still in development'}, status=status.HTTP_404_NOT_FOUND)

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
    def post(self, request):
        """Создать новый узел"""

        try:
            result = methods_model.create_node(request.data)
            return Response({'node': result}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)
