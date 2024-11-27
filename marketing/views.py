import time
import os
import tempfile
from marketing.serializer import TextToSpeechRequestSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip
from account.serializer import TextToSpeechSerializerVideo
from googletrans import Translator
from .models import TextToSpeechRequest  

from django.http import JsonResponse

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation

class TextToSpeechView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TextToSpeechSerializerVideo(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data.get('text')
            language = serializer.validated_data.get('language')
            selected_voice = serializer.validated_data.get('selectedVoice')
            video_file = serializer.validated_data.get('videoFile')

           
            if language == 'en' and not self.is_english(text):  
                translator = Translator()
                text = translator.translate(text, src='fr', dest='en').text
            elif language == 'fr' and self.is_english(text):  
                translator = Translator()
                text = translator.translate(text, src='en', dest='fr').text

            
            tts = gTTS(text=text, lang=language, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_fp:
                tts.save(audio_fp.name)

             
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as video_fp:
                    video_fp.write(video_file.read())
                    video_fp.close()

                  
                    video_clip = VideoFileClip(video_fp.name)
                    audio_clip = AudioFileClip(audio_fp.name)

                    final_clip = video_clip.set_audio(audio_clip)          
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as final_fp:
                        final_clip.write_videofile(final_fp.name, codec='libx264', audio_codec='aac')
                        final_fp.seek(0)
                        response = HttpResponse(final_fp.read(), content_type="video/mp4")
                        response['Content-Disposition'] = 'attachment; filename="synced_video.mp4"'

           
            time.sleep(2)  

          
            tts_request = TextToSpeechRequest(
                text=text,
                language=language,
                selected_voice=selected_voice,
                video_file=video_file,  
                audio_file=audio_fp.name,
                video_with_audio=final_fp.name
            )
            tts_request.save()

           
            try:
                os.remove(audio_fp.name)
                os.remove(video_fp.name)
                os.remove(final_fp.name)
            except Exception as e:
                print(f"Erreur lors de la suppression des fichiers temporaires: {e}")

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
    def is_english(self, text):
        try:
            
            translator = Translator()
            detected_lang = translator.detect(text).lang
            return detected_lang == 'en'
        except Exception as e:
            return False

class RetrieveMarketingFilesView(APIView):
    def get(self, request, *args, **kwargs):
        
        tts_requests = TextToSpeechRequest.objects.all()

       
        serializer = TextToSpeechRequestSerializer(tts_requests, many=True)

        
        return Response(serializer.data)
    



class DeleteTextToSpeechRequestView(APIView):
    def delete(self, request, pk, *args, **kwargs):
        try:
            
            tts_request = TextToSpeechRequest.objects.get(pk=pk)
            tts_request.delete()
            return Response({"message": "Text-to-speech request deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except TextToSpeechRequest.DoesNotExist:
            return Response({"error": "Text-to-speech request not found."}, status=status.HTTP_404_NOT_FOUND)

@staticmethod
def _delete_files(file_fields):
    """
    Supprime une liste de fichiers associés à des champs FileField/ImageField.

    :param file_fields: Liste des champs de fichiers.
    :return: Liste des fichiers supprimés.
    """
    deleted_files = []

    for file_field in file_fields:
        if file_field and file_field.name:  
            file_path = file_field.path  

            
            if not file_path.startswith(settings.MEDIA_ROOT):
                raise SuspiciousFileOperation(f"Tentative de suppression d'un fichier en dehors de MEDIA_ROOT: {file_path}")

            if os.path.exists(file_path):  
                try:
                    os.remove(file_path)  
                    deleted_files.append(file_path)
                except Exception as e:
                    print(f"Erreur lors de la suppression du fichier {file_path}: {e}")

    return deleted_files




class DeleteMultipleTextToSpeechRequestsView(APIView):
    def delete(self, request, *args, **kwargs):
        
        ids = request.data.get("ids", [])

        if not ids:
            return JsonResponse({"error": "Aucune ID fournie."}, status=status.HTTP_400_BAD_REQUEST)

        tts_requests = TextToSpeechRequest.objects.filter(id__in=ids)
        
        if tts_requests.count() != len(ids):
            return JsonResponse({"error": "Certaines demandes n'ont pas été trouvées."}, status=status.HTTP_404_NOT_FOUND)

        tts_requests.delete()

        return Response({"message": "Demandes supprimées avec succès."}, status=status.HTTP_204_NO_CONTENT)