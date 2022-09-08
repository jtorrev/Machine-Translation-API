from datetime import datetime
from django.db import transaction
from django.db.models import Q
from django.http.response import JsonResponse, HttpResponse, FileResponse
from django.utils.timezone import get_current_timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.decorators import parser_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from translate.models import Language, LanguagePair, Job, Translation, IN_PROGRESS
from translate.utils.xliff_utils import Parser, build_xliff, XLIFFParser
from translate.utils.translate_utils import list_qa_confidence
import json
from translate.apps import TranslateConfig
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def translate_by_id(request):
    try:
        payload = json.loads(request.body)
        print("   AcclaroMT:", payload)
        trans_id_list = payload['trans_id']
        if len(trans_id_list) == 0:
            raise Exception("No ids")
        translations = Translation.objects.filter(id__in=trans_id_list)
        text_list = []
        for trans in translations:
            text_list.append(trans.text)
        lang_pair = translations[0].lang_pair
        src_lang = lang_pair.src_lang.name_iso_639_1
        tgt_lang = lang_pair.tgt_lang.name_iso_639_1
        lang_pair_key = "{}_{}".format(src_lang, tgt_lang)
        trained_model = TranslateConfig.translate_models[lang_pair_key]
        text_trans = trained_model["model"].sample(text_list, beam=5)
        print("  --AcclaroMT FR Dibs Translation:",
              text_trans[0].replace("[{}_XX]".format(src_lang), ""))
        output_tmp_texts = []
        for sentence in text_trans:
            output_tmp_texts.append(sentence.replace("[{}_XX]".format(tgt_lang), ""))
        output_texts, engines = list_qa_confidence(source_list=text_list, target_list=output_tmp_texts,
                                                   src_lang=src_lang,
                                                   tgt_lang=tgt_lang)
        with transaction.atomic():
            tmp_date = datetime.now().astimezone(tz=get_current_timezone())
            for index, translation in enumerate(translations):
                translation.translate_text = output_texts[index]
                translation.engine = trained_model['name']
                translation.trained_model = True
                if len(engines[index]) != 0:
                    translation.external_model = engines[index]
                translation.end_date = tmp_date
                translation.save()
        return JsonResponse({
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "source_text": text_list,
                "input_language": src_lang,
                "output_language": tgt_lang,
                "output_text": output_texts
            }}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def translate(request):
    try:
        user = request.user
        payload = json.loads(request.body)
        print("   AcclaroMT:", payload)
        text_list = payload['text']
        input_lang = payload['input_language'].lower()
        output_lang = payload['output_language'].lower()
        src_lang = Language.objects.get(
            Q(name_iso_639_1=input_lang) | Q(name_iso_639_2=input_lang) | Q(other_names=input_lang))
        tgt_lang = Language.objects.get(
            Q(name_iso_639_1=output_lang) | Q(name_iso_639_2=output_lang) | Q(other_names=output_lang))
        lang_pair = LanguagePair.objects.get(src_lang__id=src_lang.id, tgt_lang_id=tgt_lang.id)
        lang_pair_key = "{}_{}".format(lang_pair.src_lang.name_iso_639_1, lang_pair.tgt_lang.name_iso_639_1)
        model = TranslateConfig.translate_models[lang_pair_key]
        translation = model["model"].sample(text_list, beam=5)
        print("  --AcclaroMT FR Dibs Translation:",
              translation[0].replace("[{}_XX]".format(src_lang.name_iso_639_1), ""))
        output_tmp_texts = []
        for sentence in translation:
            print(sentence)
            output_tmp_texts.append(sentence.replace("[{}_XX]".format(tgt_lang.name_iso_639_1), ""))
        output_texts, engines = list_qa_confidence(source_list=text_list, target_list=output_tmp_texts,
                                                   src_lang=src_lang,
                                                   tgt_lang=tgt_lang)
        with transaction.atomic():
            for index, text in enumerate(text_list):
                tmp_date = datetime.now().astimezone(tz=get_current_timezone())
                translation = Translation()
                translation.text = text
                translation.translate_text = output_texts[index]
                translation.start_date = tmp_date
                translation.characters = len(text.replace(" ", ""))
                translation.lang_pair = lang_pair
                translation.user = user
                translation.engine = model['name']
                translation.trained_model = True
                if len(engines[index]) != 0:
                    translation.external_model = engines[index]
                translation.end_date = tmp_date
                translation.save()
        return JsonResponse({
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "source_text": text_list,
                "input_language": input_lang,
                "output_language": output_lang,
                "output_text": output_texts
            }}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET', 'POST'])
# @parser_classes([XMLParser])
@parser_classes([XLIFFParser])
def xtm_translate(request):
    user = request.user
    try:
        print(request)
        current_time = datetime.now().strftime("%H:%M:%S")
        print("  >>>>>>> XTM Translate received ", current_time, " <<<<<<<<<")
        parser = Parser(request.data)
        job, sentences = parser.parse_xliff()
        print(job)
        obj = Job()
        obj.name = "name"
        obj.status = IN_PROGRESS[0]
        obj.src_lang=job['src_lang']
        obj.tgt_lang=job['tgt_lang']
        obj.mtdone = False
        src_lang_id = Language.objects.get(
            Q(name_iso_639_1=job['src_lang']) | Q(name_iso_639_2=job['src_lang']) | Q(other_names=job['src_lang'])).id
        tgt_lang_id = Language.objects.get(
            Q(name_iso_639_1=job['tgt_lang']) | Q(name_iso_639_2=job['tgt_lang']) | Q(other_names=job['tgt_lang'])).id
        lang_pair = LanguagePair.objects.get(src_lang__id=src_lang_id, tgt_lang_id=tgt_lang_id)
        obj.update_date = datetime.now().astimezone(tz=get_current_timezone())
        with transaction.atomic():
            obj.save()
            for key, value in sentences.items():
                if value is None:
                    continue
                try:
                    if '"' in value or "'" in value:
                        value = value.replace('"', '""').replace("'", "''")
                except Exception as exc:
                    print("***** error registered", exc)
                translation = Translation()
                translation.sent_id = int(key)
                translation.text = value
                translation.job = obj
                translation.characters = 0 if value is None or len(value) == 0 else len(value.replace(" ", ""))
                translation.start_date = datetime.now().astimezone(tz=get_current_timezone())
                translation.lang_pair = lang_pair
                translation.user = user
                translation.save()
        return JsonResponse({
            "status": "success",
            "code": status.HTTP_200_OK,
            "job_id": obj.id,
            "jobId": obj.id,
            "message": "success",
            "errorCode": 200
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET', 'POST'])
def status_post(request, id):
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(" ---  Status Requested:", id, "time", current_time)
        job = Job.objects.get(id=id)
        job_status = job.status
        if job_status:
            print("   Sending", job_status)
            return JsonResponse({
                "status": "success",
                "code": status.HTTP_200_OK,
                "data": {
                    "job_status": job_status
                },
                "jobStatus": job_status
            }, status=status.HTTP_200_OK)
        else:
            raise Exception("Error in Job Status")
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET', 'POST'])
@renderer_classes([XMLRenderer])
def download_post(request, id):
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        print("    <<<<<<   Download received:", current_time, " ID:", id)
        try:
            job = Job.objects.get(id=id, mtdone=True)
            sentences = Translation.objects.filter(job__id=id)
            sentence_array = []
            for sentence in sentences:
                sentence_array.append([sentence.id, sentence.sent_id, sentence.text, sentence.translate_text])
            download_result = build_xliff(sentence_array, src_lang=job.src_lang,
                                          tgt_lang=job.tgt_lang)
            print(download_result)
            return FileResponse(download_result, content_type='text/xml; charset=utf-8')
        except Job.DoesNotExist:
            raise Exception("The job does not exist with this parameters")
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)
