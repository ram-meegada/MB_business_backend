from rest_framework.views import APIView
from livestock.serializer import *
from rest_framework.response import Response
from utils.messages import *
from livestock.models import LiveStockModel


class AddLiveStockView(APIView):
    def post(self, request):
        serializer = WriteLiveStockSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": LIVE_STOCK_ADDED}, status=200)
        return Response({"data": serializer.errors, "message": WENT_WRONG}, status=400)


class ListLiveStockView(APIView):
    def get(self, request):
        try:
            stock_list = LiveStockModel.objects.only(
                'id', 'breed', 'milk_capacity', 'parity', 'qualities')
            serializer = LiveStockListSerializer(stock_list, many=True)
            return Response({"data": serializer.data, "message": "Live stock data"}, status=200)
        except Exception as err:
            return Response({"data": None, "message": WENT_WRONG}, status=400)


class GetLiveStockById(APIView):
    def get(self, request, id):
        try:
            live_stock = LiveStockModel.objects.get(id=id)
        except LiveStockModel.DoesNotExist:
            return Response({"data": None, "message": NOT_FOUND}, status=400)
        serializer = LiveStockByIdSerializer(live_stock)
        return Response({"data": serializer.data, "message": "Live stock details fetched successfully"}, status=200)
