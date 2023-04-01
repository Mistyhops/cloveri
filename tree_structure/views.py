from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import methods_model



class GetNodeApiView(APIView):
    def get(self, request, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': 'pk cannot be null'})

        result = methods_model.get_node(pk)
        if result:
            return Response({'node': result})
        else:
            return Response({'error': 'Object does not exists'})


    def put(self, request, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': 'pk cannot be null'})

        result = methods_model.update_attributes_node(request, pk)
        if result:
            return Response({'node': result}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Object does not exists'})


class GetNodesApiView(APIView):
    def get(self, request, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': 'pk cannot be null'})

        result = methods_model.get_nodes(pk)
        if result:
            return Response({'nodes': result})
        else:
            return Response({'error': 'Object does not exists'})


class NodeApiView(APIView):
    def post(self, request):
        result = methods_model.create_node(request)
        if result:
            return Response({'node': result}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Object not created'})




    # def delete(self, request):
    #     result = methods_model.create_node(request)
    #     return Response({'node': result})



