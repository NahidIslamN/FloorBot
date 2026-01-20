from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import UserAcountSerializer





class Profile_Data(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserAcountSerializer(request.user)
        return Response(
            {
                "successs":True,
                "message":f"Wellcome {request.user.full_name}",
                "profile_data":serializer.data
            }
        )
    
    def patch(self, request):
        serializer = UserAcountSerializer(instance = request.user, data=request.data, partial=True)
        user = request.user
        if serializer.is_valid():
            email = serializer.validated_data.get('email', None)
            
            if email is not None:
                user.username = email
                user.email = email
                user.save()
            serializer.save()
            return Response(
                {
                    "success":False,
                    "message":"update successfully!",
                    "errors":serializer.data
                },
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {
                    "success":False,
                    "message":"validation erros!",
                    "errors":serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
