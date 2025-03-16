from django.shortcuts import render
from rest_framework.views import APIView
from livestock.serializer import WriteLiveStockSerializer
from rest_framework.response import Response
from utils.commonUtils import *
from utils.messages import *


class AddLiveStockView(APIView):
    def post(self, request):
        serializer = WriteLiveStockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": LIVE_STOCK_ADDED})
        return Response({"data": serializer.errors, "message": WENT_WRONG})
