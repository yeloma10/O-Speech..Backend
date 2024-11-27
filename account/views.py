from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializer import *
from django.http import JsonResponse

User = get_user_model()

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserProfileView(generics.RetrieveAPIView):
    def get(self, request, id):
        try:
            user = User.objects.get(pk=id)
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                
            }
            return JsonResponse(user_data, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)



class GetAllUsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'  

    def put(self, request, id):
        try:
            user = User.objects.get(pk=id)
            serializer = UserSerializer(user, data=request.data, partial=True)  
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=200)
            return JsonResponse(serializer.errors, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        

class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    lookup_field = 'id'

    def delete(self, request, id, *args, **kwargs):
        try:
            user = User.objects.get(pk=id)
            user.delete()  
            return JsonResponse({"message": "Utilisateur supprimé avec succès"}, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "Utilisateur non trouvé"}, status=404)