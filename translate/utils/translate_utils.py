from django.conf import settings
import itertools
import requests
from scipy import spatial
from laserembeddings import Laser

print("  Loading Laser module")
laser = Laser()


def similarity(vector_1, vector_2):
    return 1 - spatial.distance.cosine(vector_1, vector_2)


def get_laser_embeddings(texts, langs):
    if len(texts) != len(langs):
        raise Exception("The size of the 'text' list does not match the size of the 'language' list.")
    if len(texts) == 0:
        raise Exception("The list size cannot be 0")
    return laser.embed_sentences(texts, lang=langs)


def translator_deepl(text, src_lang, tgt_lang):
    print("DeepL:", text)
    headers = {
        'Authorization': settings.DEEPL_KEY,
    }
    data = {
        'text': text,
        'source_lang': src_lang.upper(),
        'target_lang': tgt_lang.upper(),
    }
    response = requests.get(settings.DEEPL_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["translations"][0]["text"]
    else:
        raise Exception("Error DeepL")


def remove_consecutive_duplicates(_list: list):
    preprocessed_list = []
    for x in itertools.groupby(_list):
        preprocessed_list.append(x[0])

    return " ".join(preprocessed_list)


def list_qa_confidence(source_list, target_list, src_lang, tgt_lang, confidence=True):
    result_list = []
    engine_list = []
    for i, (source, target) in enumerate(zip(source_list, target_list)):
        target = remove_consecutive_duplicates(target.split(" "))
        print("\n - QA --- Sentence:", i, "\n     ", source, "\n     ", target)
        try:
            if source.isdecimal():
                result_list.append(source)
                engine_list.append("")
            elif source.strip() == target.strip() or len(source.split(" ")) < 3:
                print(" ---- DeepL ----")
                response = translator_deepl(source, src_lang, tgt_lang)
                engine_list.append("DeepL")
                result_list.append(response)
            elif confidence:
                # src_embeddings = laser.embed_sentences([source], lang=[src_lang])
                src_embeddings = get_laser_embeddings([source], langs=[src_lang])
                # tgt_embeddings = laser.embed_sentences([target], lang=[tgt_lang])
                tgt_embeddings = get_laser_embeddings([target], langs=[tgt_lang])
                #result = 1 - spatial.distance.cosine(src_embeddings, tgt_embeddings)
                result = similarity(src_embeddings, tgt_embeddings)
                if result < 0.7:
                    response = translator_deepl(source, src_lang, tgt_lang)
                    engine_list.append("DeepL")
                    result_list.append(response)
                else:
                    engine_list.append("")
                    result_list.append(target)
            else:
                engine_list.append("")
                result_list.append(target)
        except Exception as exc:
            engine_list.append("")
            result_list.append(target)
            print("QA Error:", exc)
    return result_list, engine_list


def chunks(lst, n):
    """Yield successive n-sized chunks from lst. Credit to
    https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
