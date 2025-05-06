from rest_framework.views import APIView
from livestock.serializer import *
from rest_framework.response import Response
from utils.messages import *
from livestock.models import LiveStockModel
from utils.commonUtils import fetch_serializer_error
from rest_framework.permissions import IsAdminUser


class AddLiveStockView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        serializer = WriteLiveStockSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": LIVE_STOCK_ADDED}, status=200)
        return Response({"data": serializer.errors, "message": WENT_WRONG}, status=400)


class ListLiveStockView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        try:
            stock_list = LiveStockModel.objects.filter(is_deleted=False, user=request.user)
            serializer = LiveStockListSerializer(stock_list, many=True)
            return Response({"data": serializer.data, "message": "Live stock data"}, status=200)
        except Exception as err:
            return Response({"data": None, "message": WENT_WRONG}, status=400)


class GetLiveStockById(APIView):
    permission_classes = [IsAdminUser]
    def get_live_stock(self, id):
        self.live_stock = LiveStockModel.objects.filter(id=id).first()

    def get(self, request, id):
        self.get_live_stock(id)

        if not self.live_stock:
            return Response({"data": None, "message": NOT_FOUND}, status=400)

        serializer = LiveStockByIdSerializer(self.live_stock)
        return Response({"data": serializer.data, "message": "Live stock details fetched successfully"}, status=200)

    def delete(self, request, id):
        self.get_live_stock(id)

        if not self.live_stock:
            return Response({"data": None, "message": NOT_FOUND}, status=400)

        self.live_stock.is_active = False
        self.live_stock.is_deleted = True
        self.live_stock.save()

        return Response({"data": None, "message": "Live stock deleted successfully"}, status=200)

    def put(self, request, id):
        self.get_live_stock(id)

        if not self.live_stock:
            return Response({"data": None, "message": NOT_FOUND}, status=400)
        serializer = WriteLiveStockSerializer(
            self.live_stock, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Details saved successfully"}, status=200)
        fetch_serializer_error(serializer.errors)
        return Response({"data": None, "message": WENT_WRONG}, status=400)
