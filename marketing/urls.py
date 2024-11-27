from django.urls import path
from .views import TextToSpeechView, RetrieveMarketingFilesView, DeleteTextToSpeechRequestView, DeleteMultipleTextToSpeechRequestsView

urlpatterns = [
    path('api/marketting/', TextToSpeechView.as_view(), name='text-to-speech'),  
    path('api/retrieve_marketing_files/', RetrieveMarketingFilesView.as_view(), name='retrieve_marketing_files'),

    
    path('delete-text-to-speech-request/<int:pk>/', DeleteTextToSpeechRequestView.as_view(), name='delete_text_to_speech_request'),

    
    path('delete-multiple-text-to-speech-requests/', DeleteMultipleTextToSpeechRequestsView.as_view(), name='delete_multiple_text_to_speech_requests'),
]
