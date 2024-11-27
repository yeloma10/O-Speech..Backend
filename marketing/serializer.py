from rest_framework import serializers
from .models import TextToSpeechRequest

class TextToSpeechRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextToSpeechRequest
        fields = ['id', 'text', 'language', 'selected_voice', 'video_file', 'audio_file', 'video_with_audio', 'timestamp']
