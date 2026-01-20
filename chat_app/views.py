from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import *
from .serializers import *
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .tasks import sent_message_to_chat
from .tasks import sent_note_to_user
from auths.models import CustomUser



class Unseen_Notifications_count(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        notifications = NoteModel.objects.filter(user=request.user, is_seen=False).count()

       
        
        return Response({"success":True,"message":"data fatched!","total_unseen_note":notifications}, status=status.HTTP_200_OK)
    


class Notifications(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        notifications = NoteModel.objects.filter(user=request.user)
        notifications_update = NoteModel.objects.filter(user=request.user,is_seen=False)
        notifications_update.update(is_seen=True)

        try:
            page = request.GET.get('page', 1)
            page_size = int(request.GET.get('page_size', 100))
       
        except (ValueError, TypeError):
            page = 1
            page_size = 100

        paginator = Paginator(notifications, page_size)

        try:
            notifications = paginator.page(page)
        except PageNotAnInteger:
            notifications = paginator.page(1)
        except EmptyPage:
            notifications = paginator.page(paginator.num_pages)

        serializer = NotificationSerializer(notifications, many=True)
        
        
        return Response({"success":True,"message":"data fatched!","data":serializer.data}, status=status.HTTP_200_OK)
    



class User_Suport_Message(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            chat = Chat.objects.filter(participants=request.user).first()
            if not chat:
                superusers = CustomUser.objects.filter(is_superuser=True)

                chat = Chat.objects.create(
                    chat_type='group',
                    name='Support DMS'
                )

                # Assign participants correctly
                chat.participants.set(superusers)
                chat.participants.add(request.user)
                chat.save()

            # Serialize chat (IMPORTANT: pass request context)
            chat_serializer = ChatListSerializer(
                chat,
                context={'request': request}
            )

            support_messages = Message.objects.filter(chat = chat).order_by("created_at")
            message_serializers = Message_List_Serializer(support_messages, many=True)

            return Response(
                {
                    "success": True,
                    "status_message": "chat fetched successfully",
                    "inbox_data": chat_serializer.data,
                    "messages":message_serializers.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "something went wrong!",
                    "errors": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )




class SuperAdminSuportChatList(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        try:
            chats = Chat.objects.order_by('-updated_at')
            chat_serializer = ChatListSerializer(
                chats,
                context={'request': request},
                many=True
            )

     
            return Response(
                {
                    "success": True,
                    "status_message": "chat fetched successfully",
                    "inbox_data": chat_serializer.data,
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "something went wrong!",
                    "errors": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )





class MessageList_Chats(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,inbox_id):
        try:
            chats = Chat.objects.get(id = inbox_id)
        except:
            return Response({"success":False,"message":"chat not found!" }, status= status.HTTP_404_NOT_FOUND)
        if request.user in chats.participants.all():
            messages = Message.objects.filter(chat = chats).order_by("created_at")


            serializers = Message_List_Serializer(messages, many=True)
                      
            return Response({"success":True,"message":"data fatched!","data":serializers.data}, status=status.HTTP_200_OK)
        else:
            return Response({"success":False,"message":"You are not a member of this chat!"}, status=status.HTTP_400_BAD_REQUEST)



class Accept_Leave_Add_People_Chat(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):

        try:
            chats = Chat.objects.get(id = pk)
        except:
            return Response({"success":False,"message":"chat not found!" }, status= status.HTTP_404_NOT_FOUND)
        if chats.invitee == request.user:
            chats.is_accepted_invitee = True
            chats.save()
            # Notify inviter about chat acceptance
            sent_note_to_user.delay(user_id=chats.inviter.id, title=f"Chat Request Accepted", content=f"{request.user.first_name} {request.user.last_name} accepted your chat request", note_type='success')
            return Response({"success":True,"message":"you are now connected!"}, status=status.HTTP_200_OK)
        else:
            return Response({"success":False,"message":"you are not able to access this!","error":"invalid message id!",}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, pk):
        try:
            chats = Chat.objects.get(id = pk)
        except:
            return Response({"success":False,"message":"chat not found!" }, status= status.HTTP_404_NOT_FOUND)
        if request.user in chats.participants.all():
            chats.participants.remove(request.user)
            chats.save()
            return Response({"success":True,"message":"successfully leave form the chat!"}, status=status.HTTP_200_OK)
        else:
            return Response({"success":False,"message":"you are no a memeber of the chat!"}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            chats = Chat.objects.get(id = pk)
        except:
            return Response({"success":False,"message":"chat not found!" }, status= status.HTTP_404_NOT_FOUND)
        if request.user in chats.participants.all():

            serializer = Add_People_Group_CreateSerializer(data=request.data)
            
            if serializer.is_valid():
                perticipance = serializer.data.get('user_list')
                # Notify newly added users
                for us in perticipance:
                    sent_note_to_user.delay(user_id=us, title=f"Added to Group", content=f"You've been added to group '{chats.name}'", note_type='normal')
                chats.chat_type = "group"
                chats.save()
                try:
                    for us in perticipance:
                        user = User.objects.get(id=us)
                        chats.participants.add(user)
                except:
                    pass
                chats.save()

                return Response({"success":True,"message":"successfully added!","user_list":perticipance}, status= status.HTTP_200_OK)
            else:
                return Response({"success":False,"messsage":"validatiaon errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({"success":False,"message":"you are not a member of the chat!"}, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk):
        try:
            chats = Chat.objects.get(id = pk)
        except:
            return Response({"success":False,"message":"chat not found!" }, status= status.HTTP_404_NOT_FOUND)
        if request.user in chats.participants.all() and chats.inviter == request.user:
            serializer = Add_People_Group_CreateSerializer(data=request.data)
            if serializer.is_valid():
                perticipance = serializer.data.get('user_list')
                # Notify removed users
                for us in perticipance:
                    sent_note_to_user.delay(user_id=us, title=f"Removed from Group", content=f"You've been removed from group '{chats.name}'", note_type='warning')
                chats.chat_type = "group"
                try:
                    for us in perticipance:
                        user = User.objects.get(id=us)
                        chats.participants.remove(user)
                except:
                    pass

                return Response({"success":True,"message":"successfully removed!","user_list":perticipance}, status= status.HTTP_200_OK)
            else:
                return Response({"success":False,"messsage":"validatiaon errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 
        else:
            return Response({"success":False,"message":"you can't remove a user from this chat!"}, status=status.HTTP_400_BAD_REQUEST)
    



class Sent_Message_Chats(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            chat = Chat.objects.get(id=pk)
        except Chat.DoesNotExist:
            return Response({
                "success": False,
                "message": "chat not found!"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.user not in chat.participants.all():
            return Response({
                "success": False,
                "message": "you are not a member of this chat!"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = Send_Message_Serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "validation errors!",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        message_text = serializer.validated_data.get("message", "").strip()
        files = request.FILES.getlist('files') if 'files' in request.FILES else []
        
        # Validate: message must have text or files
        if not message_text and not files:
            return Response({
                "success": False,
                "message": "message must contain either text or files"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create message
            message_obj = Message.objects.create(
                chat=chat,
                sender=request.user,
                text=message_text if message_text else None
            )
            
            # Attach files to message
            for file in files:
                try:
                    msg_file = MessageFiles.objects.create(
                        title=file.name,
                        file=file
                    )
                    message_obj.files.add(msg_file)
                except Exception as e:
                    print(f"Error saving file {file.name}: {str(e)}")
                    continue
            
            # Update chat timestamp
            chat.save()
            
            # Serialize and return response
            message_serializer = Message_List_Serializer(message_obj)

            sent_message_to_chat.delay(chat.id, message_serializer.data)
            return Response({
                "success": True,
                "message": "message sent successfully!",
                "data": message_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                "success": False,
                "message": "error sending message",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        



    
