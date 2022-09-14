from django.apps import AppConfig
from django.conf import settings
from fairseq.models.bart import BARTModel

# UK
from translate.utils.bijective_map import uk_us, undo, helper
import re
from functools import partial


class ModelENUStoENUK(object):

    def __init__(self):
        print('Loading UK-US dictionary...')
        self.UK = 'uk'
        self.US = 'us'
        self.repl_dict = dict(uk_us)
        self.repl_dict = {v: k for k, v in self.repl_dict.items()}
        for key, value in self.repl_dict.copy().items():
            capital_key = key.capitalize()
            capital_value = value.capitalize()

            upper_key = key.upper()
            upper_value = value.upper()

            lower_key = key.lower()
            lower_value = value.lower()
            if capital_key not in self.repl_dict:
                self.repl_dict[capital_key] = capital_value
            if upper_key not in self.repl_dict:
                self.repl_dict[upper_value] = upper_value
            if lower_key not in self.repl_dict:
                self.repl_dict[lower_key] = lower_value
        self.word_re = re.compile(r'\b[a-zA-Z]+\b')

    def sample(self, texts, **kwargs):
        return [self.word_re.sub(partial(helper, self.repl_dict), text) for text in texts]


class TranslateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'translate'
    translate_models = {}

    def ready(self):
        for model, value in settings.MODELS.items():
            self.translate_models[model] = {}
            self.translate_models[model]["name"] = value['name']
            print("    -- URL --> {}".format(value["url"]))
            model_loaded = ModelENUStoENUK()
            # model_loaded = BARTModel.from_pretrained(
            #     value["url"],
            #     checkpoint_file='model.pt',
            #     bpe='sentencepiece',
            #     sentencepiece_vocab=f'{value["url"]}/sentencepiece.bpe.model', share_all_embeddings=False)
            # model_loaded.eval()
            # model_loaded.cuda()
            self.translate_models[model]["model"] = model_loaded
            print("    -- en-deDibs model loaded successfully")
        self.translate_models["en_XX_en_GB"] = {}
        self.translate_models["en_XX_en_GB"]["name"] = "replace"
        self.translate_models["en_XX_en_GB"]["model"] = ModelENUStoENUK()
