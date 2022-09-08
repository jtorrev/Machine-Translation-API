from django.apps import AppConfig
from django.conf import settings
from fairseq.models.bart import BARTModel

class TestModel(object):

    def sample(self,objs,beam):
        return ["test" for obj in objs]

class TranslateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'translate'
    translate_models = {}

    def ready(self):
        for model, value in settings.MODELS.items():
            self.translate_models[model] = {}
            self.translate_models[model]["name"] = value['name']
            print("    -- URL --> {}".format(value["url"]))
            model_loaded = TestModel()
            # model_loaded = BARTModel.from_pretrained(
            #     value["url"],
            #     checkpoint_file='model.pt',
            #     bpe='sentencepiece',
            #     sentencepiece_vocab=f'{value["url"]}/sentencepiece.bpe.model', share_all_embeddings=False)
            # model_loaded.eval()
            # model_loaded.cuda()
            self.translate_models[model]["model"] = model_loaded
            print("    -- en-deDibs model loaded successfully")
            #
