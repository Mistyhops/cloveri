from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import methods_model



class GetNodesApiView(APIView):
    def get(self, request):
        result = methods_model.get_all_node()
        return Response({'nodes': result}, status=status.HTTP_200_OK)

class NodeApiView(APIView):
    def post(self, request):
        result = methods_model.create_node(request)
        return Response({'node': result}, status=status.HTTP_201_CREATED)



