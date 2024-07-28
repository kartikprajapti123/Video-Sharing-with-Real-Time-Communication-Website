import threading
from django.db import transaction
from django.shortcuts import render
from user.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from user.serializer import RegisterSerializer
from rest_framework import status
from utils.register_email_verfication import (
    send_email_verfication,
    send_reset_password_mail,
)
from decouple import config
from django.contrib.auth.hashers import check_password
from utils.generate_verify_token import generate_token, decode_token
from utils.generate_otp import generate_otp
import json
import requests


class RegisterViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                email = serializer.validated_data["email"]
                user = User.objects.filter(email=email).first()

                if user and not user.email_verified:
                    # User exists but email is not verified, update OTP and resend email
                    user.otp = generate_otp()
                    print(user.otp)
                    user.save()
                else:
                    # Create a new user
                    user = serializer.save()
                    print(user.otp)

                token = generate_token(email, 60)
                subject = "Email Verification"
                to = email
                context = {
                    "link": f"{config('HOST_URL')}verify-otp/{token}/",
                    "otp": user.otp,
                }
                # send_email_verfication(subject=subject, to=to, context=context)
                email_thread = threading.Thread(
                    target=send_email_verfication, args=(subject, to, context)
                )
                email_thread.start()
                return Response(
                    {
                        "success": True,
                        "message": "Otp and verification link are send to your mail",
                        "data": serializer.data,
                        "token": token,
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


@method_decorator(csrf_exempt, name="dispatch")
class VerifyEmailViewset(ModelViewSet):
    queryset = User.objects.all()

    @transaction.atomic()
    def create(self, request, token, *args, **kwargs):
        otp = request.data.get("otp")
        try:
            payload = decode_token(token)
        except Exception:
            return Response(
                {"success": False, "message": "Link Expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if "email" not in payload:
            return Response(
                {"success": False, "message": "Invalid Link"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = User.objects.filter(email=payload["email"]).first()
        print(user.otp)
        if user is None:
            return Response(
                {"success": False, "message": "Email is not registered"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not (user.otp == otp):
            return Response(
                {"success": False, "message": "Invalid otp"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.email_verified = True
        user.otp = otp
        user.save()

        return Response(
            {"success": True, "message": "Email successfully verified"},
            status=status.HTTP_200_OK,
        )


class ResendOtpViewSet(ModelViewSet):

    @transaction.atomic()
    def create(self, request, token, *args, **kwargs):
        try:
            payload = decode_token(token)
        except Exception:
            return Response(
                {"success": False, "message": "Link Expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if "email" not in payload:
            return Response(
                {"success": False, "message": "Invalid Link"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = User.objects.filter(email=payload["email"]).first()
        if user is None:
            return Response(
                {"success": False, "message": "Email is not registered"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        otp = generate_otp()
        token = generate_token(user.email, 60)
        subject = "Email Verification"
        to = user.email
        context = {"link": f"{config('HOST_URL')}verify-otp/{token}/", "otp": otp}
        # send_email_verfication(subject=subject, to=to, context=context)
        email_thread = threading.Thread(
            target=send_email_verfication, args=(subject, to, context)
        )
        email_thread.start()

        return Response(
            {"success": True, "message": "An OTP has been sent again to your address."},
            status=status.HTTP_200_OK,
        )


class LoginViewSet(ModelViewSet):

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "Invalid Email or Password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if check_password(password, user.password):
            if user.email_verified:
                refresh_token = RefreshToken.for_user(user)
                access_token = str(refresh_token.access_token)

                return Response(
                    {
                        "success": True,
                        "message": "Login successful done",
                        "token": {
                            "access_token": access_token,
                            "refresh_token": str(refresh_token),
                        },
                        "data": {
                            "id": user.id,
                            "email": user.email,
                            "username": user.username,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "success": False,
                        "message": "Otp is not Verified ! Check your mail inbox ",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"success": False, "message": "Invalid Email or Password"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    permission_classes = [AllowAny]

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "Email address not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.email_verified:
            return Response(
                {
                    "success": False,
                    "message": "Otp is not Verified ! Check your mail inbox ",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = generate_token(user.email, 60)
        to = user.email
        subject = "Reset Password"
        context = {"link": f"{config('HOST_URL')}reset-password/{token}/"}

        email_thread = threading.Thread(
            target=send_reset_password_mail, args=(subject, to, context)
        )
        email_thread.start()

        return Response(
            {"success": True, "message": "Password reset link sent to your email"},
            status=status.HTTP_200_OK,
        )


class ResetPasswordViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("-id")

    @transaction.atomic()
    def create(self, request, token, *args, **kwargs):
        password = request.data.get("password")
        password2 = request.data.get("password2")

        try:
            payload = decode_token(token)
        except Exception:
            return Response(
                {"success": False, "message": "Link expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "email" not in payload:
            return Response(
                {"success": False, "message": "Invalid link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=payload["email"]).first()
        if not user:
            return Response(
                {"success": False, "message": "Email address not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if len(password) < 8 or len(password) > 14:
            return Response(
                {
                    "success": False,
                    "message": "Password length should be between 8 and 14 characters",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != password2:
            return Response(
                {"success": False, "message": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()

        return Response(
            {"success": True, "message": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


class ChangePasswordViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        password = request.data.get("password")
        password2 = request.data.get("password2")

        if len(password) < 8 or len(password) > 14:
            return Response(
                {
                    "success": False,
                    "message": "Password length should be between 8 to 14",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != password2:
            return Response(
                {
                    "success": False,
                    "message": "password and Re-Password is not matching ",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)

        except Exception:
            return Response(
                {"success": False, "message": "Email is not Registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()

        return Response(
            {"success": True, "message": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


class LoginWithGoogleViewSet(ModelViewSet):
    queryset = User.objects.all()

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        token = request.data.get("token")
        if token:
            try:
                response = requests.get(
                    f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
                )

                if response.status_code == 200:
                    user_info = response.json()
                    print(user_info)

                    email = user_info["email"]
                    username = user_info["name"]

                    user = User.objects.filter(email=email)
                    if user.exists():
                        user[0].is_active=True
                        user[0].save()
                        refresh_token = RefreshToken.for_user(user[0])
                        access_token = str(refresh_token.access_token)

                        return Response(
                            {
                                "success": True,
                                "message": "Google authentication Successfully done",
                                "token": {
                                    "access_token": access_token,
                                    "refresh_token": str(refresh_token),
                                },
                            },
                            status=status.HTTP_200_OK,
                        )
                        
                    else:
                        user=User.objects.create(email=email,username=username)
                        user.is_active=True
                        user.set_password("password@123")
                        user.email_verified=True
                        user.save()

                    # Process user info, create user, or authenticate user as needed
                    return Response(
                        {
                            "success": False,
                            "message": "Google authentication successfully done",
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                    )

            except requests.exceptions.RequestException as e:
                return Response(
                    {"success": False, "message": "Something went wrong ! try again"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {"success": False, "message": "Something went wrong ! Try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )
