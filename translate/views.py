from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.db import transaction
from django.conf import settings
from django.db.models import Q
import requests
from datetime import datetime
from django.utils.timezone import get_current_timezone
from translate.models import Translation
from translate.utils.translate_utils import translator_deepl


# Create your views here.
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def deepl_translate(request):
    user = request.user
    try:
        target = request.data
        text = target['text']
        src_lang = target['input_language'].lower()
        tgt_lang = target['output_language'].lower()
        src_lang = settings.LANGUAGES_DICT[src_lang]
        tgt_lang = settings.LANGUAGES_DICT[tgt_lang]
        output_texts = []
        for tmp_text in text:
            translated_text = translator_deepl(tmp_text, settings.LANGUAGES_DEEPL[src_lang], settings.LANGUAGES_DEEPL[tgt_lang])
            output_texts.append(translated_text)
        result = {
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "source_text": text,
                "input_language": src_lang,
                "output_language": tgt_lang,
                "output_text": output_texts
            }}
        with transaction.atomic():
            for index, tmp_text in enumerate(text):
                tmp_date = datetime.now().astimezone(tz=get_current_timezone())
                translation = Translation()
                translation.text = tmp_text
                translation.translate_text = output_texts[index]
                translation.src_lang = src_lang
                translation.tgt_lang = tgt_lang
                translation.characters = len(tmp_text.replace(" ", ""))
                translation.start_date = tmp_date
                translation.end_date = tmp_date
                translation.engine = "DeepL"
                translation.trained_model = False
                translation.user = user
                translation.save()
        return JsonResponse(result, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": e,
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)
