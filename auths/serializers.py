from rest_framework import serializers
from .models import CustomUser




class UsermodelSignupSerializer(serializers.ModelSerializer): # Serializer for Create User object
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create(
            full_name = validated_data['full_name'],
            username = validated_data['email'],
            email = validated_data['email'],
        )
        
        user.set_password(validated_data['password'])
        user.save()
        return (validated_data)


class UsermodelSignupSerializerView(serializers.ModelSerializer): # Serializer for Create User object
    class Meta:
        model = CustomUser
        fields = ["id",'full_name', 'username', 'email', "image"]

   
    
    
class OTPSerializer(serializers.Serializer): # serializer for veryfy otp
    otp = serializers.CharField()

class OTPSerializerandPasswword(serializers.Serializer): # serializer for veryfy otp
    otp = serializers.CharField()
    password = serializers.CharField()

class LoginSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class ChangePassword_serializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()