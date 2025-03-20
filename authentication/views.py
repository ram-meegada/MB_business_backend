from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from authentication.models import UserModel
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user = UserModel.objects.get(username=request.data["username"])
        except UserModel.DoesNotExist:
            return Response({"data": None, "message": "User not found"}, status=400)
        password_verification = check_password(
            request.data["password"], user.password)
        if password_verification:
            access_token = RefreshToken.for_user(user).access_token
            return Response({"data": str(access_token), "message": "Login successful"}, status=200)
        else:
            return Response({"data": None, "message": "Incorrect password"}, status=400)
