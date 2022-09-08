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
from translate.models import Translation, Language, LanguagePair


# Create your views here.
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def deepl_translate(request):
    user = request.user
    try:
        target = request.data
        text = target['text']
        src_lang = target['input_language']
        tgt_lang = target['output_language']
        register = True #if 'register' in target.keys() and target['register'] else False
        src_lang_id = Language.objects.get(Q(name_iso_639_1=src_lang) | Q(name_iso_639_2=src_lang)).id
        tgt_lang_id = Language.objects.get(Q(name_iso_639_1=tgt_lang) | Q(name_iso_639_2=tgt_lang)).id
        lang_pair = LanguagePair.objects.get(src_lang__id=src_lang_id, tgt_lang_id=tgt_lang_id)
        print("DeepL:", text)
        headers = {
            'Authorization': settings.DEEPL_KEY,
        }
        output_texts = []
        for tmp_text in text:
            data = {
                'text': tmp_text,
                'source_lang': src_lang.upper(),
                'target_lang': tgt_lang.upper(),
            }
            response = requests.get(settings.DEEPL_URL, headers=headers, data=data)
            output_texts.append(response.json()["translations"][0]["text"])
        result = {
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "source_text": text,
                "input_language": src_lang,
                "output_language": tgt_lang,
                "output_text": output_texts
            }}
        if register:
            with transaction.atomic():
                for index, tmp_text in enumerate(text):
                    tmp_date = datetime.now().astimezone(tz=get_current_timezone())
                    translation = Translation()
                    translation.text = tmp_text
                    translation.translate_text = output_texts[index]
                    translation.lang_pair = lang_pair
                    translation.characters = len(text.replace(" ", ""))
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
