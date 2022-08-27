import requests
from django.shortcuts import render
from django.http import FileResponse,HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
@permission_classes((AllowAny,))
def translator_deepl(text, src_lang, tgt_lang):
    print("DeepL:", text)
    headers = {
        'Authorization': 'DeepL-Auth-Key 3b78df08-6078-f54e-83b6-a1980170904b',
    }

    data = {
        'text': text,
        'source_lang': src_lang.upper(),
        'target_lang': tgt_lang.upper(),
    }

    response = requests.get('https://api.deepl.com/v2/translate', headers=headers, data=data)

    result = {
        "translation": {
            "input_language": src_lang,
            "output_language": tgt_lang,
            "output_text": response.json()["translations"][0]["text"]
        }}
    print("", response.json()["translations"][0]["text"])
    return result