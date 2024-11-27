from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from gtts import gTTS
from io import BytesIO
from account.serializer import TextToSpeechSerializer
from googletrans import Translator
from rest_framework import status  

from education.models import Parametre_vocal
from .serializer import ParametreVocalSerializer  


def is_english(text):
    return detect_language(text) == 'en'


def is_spanish(text):
    return detect_language(text) == 'es'


def is_german(text):
    return detect_language(text) == 'de'


def detect_language(text):
    try:
        translator = Translator()
        detected_lang = translator.detect(text).lang
        return detected_lang
    except Exception as e:
        return 'unknown' 
    
@api_view(['POST'])
def text_to_speech(request):
    if request.method == 'POST':
        serializer = TextToSpeechSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data['text']
            language = serializer.validated_data['language']
            selected_voice = serializer.validated_data['selectedVoice']

            tts_request = Parametre_vocal.objects.create(
                text=text,
                language=language,
                selected_voice=selected_voice
            )
            tts_request.save()

            
            if language == 'en' and not is_english(text):  
                text = translate_text(text, src='fr', dest='en')
            elif language == 'fr' and is_english(text):  
                text = translate_text(text, src='en', dest='fr')
            elif language == 'es' and not is_spanish(text):  
                text = translate_text(text, src='fr', dest='es')
            elif language == 'de' and not is_german(text): 
                text = translate_text(text, src='fr', dest='de')

            try:
                
                tts = gTTS(text=text, lang=language, slow=False)
                speech_file = BytesIO()
                tts.write_to_fp(speech_file)
                speech_file.seek(0)

                response = HttpResponse(speech_file, content_type='audio/mp3')
                response['Content-Disposition'] = 'attachment; filename="speech.mp3"'
                
                return response
            except Exception as e:
                return JsonResponse({'error': f"Text-to-speech conversion failed: {str(e)}"}, status=500)
        else:
            return JsonResponse(serializer.errors, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def translate_text(text, src, dest):
    try:
        translator = Translator()
        translated_text = translator.translate(text, src=src, dest=dest).text
        return translated_text
    except Exception as e:
        return JsonResponse({'error': f"Translation failed: {str(e)}"}, status=500)


class ParametreVocalList(APIView):
    def get(self, request):
        parametres = Parametre_vocal.objects.all()  
        serializer = ParametreVocalSerializer(parametres, many=True)  
        return Response(serializer.data)

@api_view(['DELETE'])
def delete_parametre_vocal(request, pk=None):
    """
    Supprime un ou plusieurs paramètres vocaux dans la base de données.

    - Si `pk` est fourni, il supprime le paramètre vocal correspondant.
    - Si `pk` n'est pas fourni, il supprime tous les paramètres vocaux.
    """
    if pk:
        try:
           
            parametre = Parametre_vocal.objects.get(pk=pk)
            parametre.delete()
            return Response({'message': f'Paramètre vocal avec ID {pk} supprimé avec succès.'}, status=status.HTTP_200_OK)
        except Parametre_vocal.DoesNotExist:
            return Response({'error': f'Aucun paramètre vocal trouvé avec ID {pk}.'}, status=status.HTTP_404_NOT_FOUND)
    else:
      
        Parametre_vocal.objects.all().delete()
        return Response({'message': 'Tous les paramètres vocaux ont été supprimés avec succès.'}, status=status.HTTP_200_OK)
