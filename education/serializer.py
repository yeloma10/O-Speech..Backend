from rest_framework import serializers
from .models import Parametre_vocal  


class TextToSpeechSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=5000)  
    language = serializers.CharField(max_length=10)  
    selectedVoice = serializers.CharField(max_length=10)  
    speed = serializers.IntegerField(min_value=1, max_value=200, required=False)  
    username = serializers.IntegerField()  

    def validate_language(self, value):
        valid_languages = ['en', 'fr', 'es', 'de']
        if value not in valid_languages:
            raise serializers.ValidationError(f"Invalid language code: {value}")
        return value

class ParametreVocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parametre_vocal
        fields = '__all__'  
