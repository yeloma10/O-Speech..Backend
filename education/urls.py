from django.urls import path
from .views import ParametreVocalList, text_to_speech, delete_parametre_vocal

urlpatterns = [
    path('text-to-speech/', text_to_speech, name='text_to_speech'),
    path("api/all/", ParametreVocalList.as_view(), name="get-all-education"),

     path('delete-parametre-vocal/', delete_parametre_vocal, name='delete_all_parametres'),
    path('delete-parametre-vocal/<int:pk>/', delete_parametre_vocal, name='delete_parametre_by_id'),
]
