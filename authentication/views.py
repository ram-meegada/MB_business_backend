from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from authentication.models import UserModel
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from authentication.serializer import UserDetailsSerializer
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView


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
            token = RefreshToken.for_user(user)
            data = {}
            data["id"] = user.pk
            data["username"] = user.username
            data["role"] = user.role
            data["access_token"] = str(token.access_token)

            response = Response({"data": data, "message": "Login successful"}, status=200)
            response.set_cookie(
                key='refresh_token',
                value=str(token),
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite="None"
            )
            return response
        else:
            return Response({"data": None, "message": "Incorrect password"}, status=400)


class AdminDetailsByToken(APIView):
    def get(self, request):
        serializer = UserDetailsSerializer(request.user)
        return Response({"data": serializer.data, "message": "Admin details"}, status=200)


class GenerateAccessByRefresh(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(status=401)

        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)

        return response
