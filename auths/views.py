
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import authenticate
import random
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from .tasks import sent_email_to
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests


# Create your views here.

class SignupView(APIView):
    def post(self, request):
        serializers = UsermodelSignupSerializer(data = request.data)
        email = serializers.initial_data['email']
        user = CustomUser.objects.filter(email=email).first()
        
        if user and user.is_email_varified==False:
            user.email = email
            user.set_password(serializers.initial_data['password'])
            user.full_name = serializers.initial_data['full_name']
            otp = f"{random.randint(0, 999999):06}"
            subject = 'Verification'
            plain_message = f"your otp is {otp}"
            sent_email_to.delay(email= user.email, text = plain_message, subject=subject)
            user.otp = otp
            user.save()
           
            return Response({ "success": True, "message": "user create successfully!"},status=status.HTTP_201_CREATED)
            
        if serializers.is_valid():
            user = serializers.save()
            otp = f"{random.randint(0, 999999):06}"
            subject = 'Verification'
            plain_message = f"your otp is {otp}"
            sent_email_to.delay(email= user['email'], text = plain_message, subject=subject)
            user = CustomUser.objects.get(email = serializers.data["email"])
            user.otp = otp
            user.save()
            return Response({ "success": True, "message": "user create successfully!"},status=status.HTTP_201_CREATED)

        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    

class Verify_Email_Signup(APIView):
    def post(self,request, email):
        serializers = OTPSerializer(data = request.data)
        if serializers.is_valid():
            try:
                user = CustomUser.objects.get(email = email)
                otp = user.otp
                if serializers.data['otp'] == otp:
                    user.is_email_varified = True
                    otp = str(random.randint(000000, 999999))
                    user.otp = otp
                    user.save()
                    return Response({"message":"verifyed successfully"}, status = status.HTTP_200_OK)
                else:
                    return Response({"success":False,"message":"wrong varification code!"}, status=status.HTTP_400_BAD_REQUEST)

            except CustomUser.DoesNotExist:
                return Response({"success":False,"message":"user not found"},status=status.HTTP_400_BAD_REQUEST)

        return Response({"success":False,"message":"validation errors","errors":serializers.errors}, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self,request):
        serializer = LoginSerializers(data = request.data)
        if serializer.is_valid():
            user = authenticate(username = serializer.data['username'], password = serializer.data['password'])
            if user:
                if user.is_email_varified:
                    refresh = RefreshToken.for_user(user)

                    user_data = UsermodelSignupSerializerView(user)

                    response = Response(
                        {
                            "success": True,
                            "message": "login successful!",
                            "access": str(refresh.access_token),
                            "user":user_data.data
                        },
                        status=status.HTTP_200_OK
                    )

                    response.set_cookie(
                        key="refresh_token",
                        value=str(refresh),
                        httponly=True, 
                        secure=True,
                        samesite="Lax",
                        max_age=24 * 60 * 60*30 
                    )

                    return response
                
               
                
                otp = f"{random.randint(0, 999999):06}"
                subject = 'Verification'
                plain_message = f"your otp is {otp}"
                sent_email_to.delay(email= user.email, text = plain_message, subject=subject)
                user.otp = otp
                user.save()

                
                return Response(
                    {
                        "success":False,
                        "message":"We sent an otp to your email! verify your first then login", 
                        
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                    
                )

            return Response({"success":False,"message":"username or password Invalid!"}, status=status.HTTP_400_BAD_REQUEST)   
        return Response({"success":False,"message":"validation errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user        
        serializer =  ChangePassword_serializer(data = request.data)
        if serializer.is_valid():
            hash_password = user.password
            raw_password = serializer.data['old_password']
            if check_password(raw_password, hash_password):
                user.set_password(serializer.data['new_password'])
                user.save()
                return Response({"message":"Password changed successfully!"}, status= status.HTTP_200_OK)
            else:
                return Response({"message":"worng old password!"}, status=status.HTTP_400_BAD_REQUEST )
        return Response({"success":False, "message":"validation errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    


class FogetPasswordView(APIView):
    def post(self, request):
        serializer = ForgetPasswordSerializer(data = request.data)
        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(email = serializer.validated_data['email'])
                otp = f"{random.randint(0, 999999):06}"
                user.otp = otp
                user.save()
                subject = 'Verification'
                plain_message = f"your otp is {otp}"
                sent_email_to.delay(email= serializer.validated_data['email'], text = plain_message, subject=subject)
                return Response(
                    {
                        "success":True,
                        "message":"we sent a otp in your email! verify the otp first",
                        "errors":serializer.errors
                    },
                    status=status.HTTP_200_OK
                    )
            except CustomUser.DoesNotExist:
                return Response({"success":False,"message":"user not found!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"success":False, "message":"validation errors", "errors":serializer.errors }, status= status.HTTP_400_BAD_REQUEST)
        


class Verify_User_ForgetPassword(APIView):
    def post(self, request, email):
        serializer = OTPSerializer(data = request.data)
        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(email = email)
                otp = user.otp
                if serializer.data['otp'] == otp:
                    refresh = RefreshToken.for_user(user)
                    otp = str(random.randint(000000, 999999))
                    user.otp = otp
                    user.save()
                    return Response( {
                        "success":True,
                        "message":"verified successfull!",
                        'access': str(refresh.access_token)                      
                    },status=status.HTTP_200_OK)
                else:
                    return Response({"success":False,"message":"wrong varification code!"}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({"success":False,"message":"User not found!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success":False,"message":"validation errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        serializer = ResetPasswordSerializer(data = request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response({ "success": True, "message": "password reset successfully", "data": None }, status=status.HTTP_200_OK)
        return Response({ "success": False, "message": "validation error!", "errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)



def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "success":True,
        "message":"login success",
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        
    }

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("id_token")
        print(token)    
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            email = idinfo.get("email")
            owner_name = idinfo.get("name")
            users, created = CustomUser.objects.get_or_create(email=email)
            users.first_name=owner_name
            users.defaults={"email": email}
            users.username = email
            users.is_email_verified=True
            users.save()
            return Response(generate_tokens_for_user(users), status=status.HTTP_200_OK)
        except:
            return Response({"success":False,"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
