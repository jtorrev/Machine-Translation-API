from django.db import transaction
from django.conf import settings
from rest_framework.authtoken.models import Token
from translate.models import Language, LanguagePair, Job, Translation, IN_PROGRESS, COMPLETED
from translate.utils.translate_utils import chunks, list_qa_confidence
from django.utils.timezone import get_current_timezone
from datetime import datetime
import requests
import json
import time


def translate_undone_jobs():
    while True:
        try:
            undone_jobs = Job.objects.filter(mtdone=False)
            for job in undone_jobs:
                undone_translations = Translation.objects.filter(job__id=job.id, translate_text__isnull=True)
                if len(undone_translations) > 0:
                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    print("\nTranslating at:", current_time, "Size:", len(undone_translations))
                    # removetable = str.maketrans('', '', '⎟””\n')
                    # sentences = []
                    trans_id = []
                    for i, translation in enumerate(undone_translations):
                        # sentences.append(
                        #     translation.text.translate(removetable).encode("ascii", errors="ignore").decode())
                        trans_id.append(translation.id)
                    print("     translating", len(undone_translations))
                    token, created = Token.objects.get_or_create(user=undone_translations[0].user)
                    headers = {'Authorization': "Token {}".format(token.key)}
                    payload = {
                        "trans_id": trans_id
                    }
                    r = requests.post(
                        "http://localhost:{}/".format(settings.SERVER_PORT) + "translate/m2-translator-ids",
                        data=json.dumps(payload), headers=headers)
                    if r.status_code == 200:
                        result = r.json()
                        print(" -- Output:", result)
                        time.sleep(0.1)
                    else:
                        raise Exception("Error")
                with transaction.atomic():
                    job.mtdone = True
                    job.status = COMPLETED[0]
                    job.end_date = datetime.now().astimezone(tz=get_current_timezone())
                    job.save()
        except Exception as e:
            print("****** Error", e)

        print("------- Sleeping for the next 5 seconds ----------")
        time.sleep(5)
