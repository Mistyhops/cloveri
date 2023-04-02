from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import methods_model


class GetNodeApiView(APIView):
    def get(self, request, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': 'pk cannot be null'})
        try:
            result = methods_model.get_node(pk)
            return Response({'node': result})
        except Exception as e:
            return Response({'error': f'{e}'})


    def put(self, request, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': 'pk cannot be null'})

        try:
            result = methods_model.update_attributes_node(request, pk)
            return Response({'node': result}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'{e}'})


class GetNodesApiView(APIView):
    def get(self, request, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': 'pk cannot be null'})

        try:
            result = methods_model.get_children(pk)
            return Response({'nodes': result})
        except TypeError as e:
            return Response({'error': f'{e}'})
        except Exception as e:
            return Response({'error': f'{e}'})


class CreateNodeApiView(APIView):
    def post(self, request):
        try:
            result = methods_model.create_node(request)
            return Response({'node': result}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'{e}'})





