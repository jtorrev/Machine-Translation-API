# from datetime import datetime
# from django.db import transaction
# from django.db.models import Q
# from django.http.response import JsonResponse, FileResponse
# from django.utils.timezone import get_current_timezone
# from rest_framework import status
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.decorators import api_view, permission_classes, authentication_classes
# from rest_framework.decorators import parser_classes, renderer_classes
# from rest_framework.permissions import IsAuthenticated
# from translate.models import Job, Translation, IN_PROGRESS, ERROR
# from django.db.models import Avg, Max, Min, Sum, Count
#
#
# # Create your views here.
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# @api_view(['GET', 'POST'])
# def stats(request):
#     user = request.user
#     try:
#         characters = Translation.objects.filter(translate_text__isnull=False).aggregate(
#             characters_sum=Sum("characters"), characters_avg=Avg("characters"))
#         characters_sum = characters["characters_sum"]
#         characters_avg = characters["characters_avg"]
#         total_translations = Translation.objects.aggregate(total=Count("id"))["total"]
#         lang_pairs = LanguagePair.objects.filter(translation__translate_text__isnull=False).annotate(
#             Count('translation__id'))
#         total_lang_pair = {}
#         total_valid_translations = 0
#         for l_pair in lang_pairs:
#             if l_pair.translation__id__count > 0:
#                 lang_pair_key = "{}_{}".format(l_pair.src_lang.name_iso_639_1, l_pair.tgt_lang.name_iso_639_1)
#                 total_lang_pair[lang_pair_key] = l_pair.translation__id__count
#                 total_valid_translations += l_pair.translation__id__count
#         return JsonResponse({
#             "status": "success",
#             "code": status.HTTP_200_OK,
#             "message": "success",
#             "data": {
#                 "translations":total_translations,
#                 "translated":total_valid_translations,
#                 "characters": characters_sum,
#                 "characters (mean)": round(characters_avg, 2),
#                 "lang_pairs": total_lang_pair
#             }
#         }, status=status.HTTP_200_OK)
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({
#             "status": "error",
#             "message": str(e),
#             "code": status.HTTP_400_BAD_REQUEST,
#             "data": {}
#         }, status=status.HTTP_400_BAD_REQUEST)
