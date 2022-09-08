import hashlib
import xml.dom.minidom as md

BUF_SIZE = 65536  # lets read stuff in 64kb chunks
sha1 = hashlib.sha1()


class Parser:
    def __init__(self, xliff):
        self.xliff = xliff

    def parse_xliff(self):
        job = {}
        sentences = {}

        dom = md.parseString(self.xliff)
        sources = dom.getElementsByTagName('trans-unit')
        file_tag = dom.getElementsByTagName('file')

        for tag in file_tag:
            source_lang = tag.getAttribute('source-language')
            job['src_lang'] = source_lang
            target_lang = tag.getAttribute('target-language')
            job['tgt_lang'] = target_lang

        for c in sources:
            for parts in c.childNodes:
                if parts.nodeType == parts.ELEMENT_NODE:
                    if parts.tagName == 'source':
                        try:
                            sentences[c.getAttribute('id')] = parts.childNodes[0].nodeValue
                        except:
                            continue

        return job, sentences


def build_xliff(sentences, src_lang, tgt_lang):
    try:
        start_result = '''<?xml version="1.0" encoding="UTF-8"?>
            <xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
                   <file source-language="''' + src_lang + '" target-language="' + tgt_lang + '''" datatype="xml">
                       <body> '''
        str_result = ''
        for sent in sentences:
            if sent[3] is not None and sent[3]:
                str_result += '''
                        <trans-unit id="''' + str(sent[1]) + '''">
                                <alt-trans  origin="AcclaroMT">
                                    <target>''' + sent[3] + '''</target>
                                </alt-trans>
                            </trans-unit>'''
            else:
                str_result += '''
                        <trans-unit id="''' + str(sent[1]) + '''">
                                <alt-trans  origin="AcclaroMT">
                                    <target>''' + " " + '''</target>
                                </alt-trans>
                            </trans-unit>'''
        end_result = '''
                        </body>
                   </file>
               </xliff>
               '''
        print("Sending back:", src_lang, tgt_lang, "\n", start_result + str_result + end_result)
        print()
        return start_result + str_result + end_result
    except Exception as exc:
        raise Exception("----- Build Output Error:", exc)


"""
Provides XML parsing support.
"""
import datetime
import decimal

from django.conf import settings
from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser


class XLIFFParser(BaseParser):
    """
    XML parser.
    """

    # media_type = "application/xliff+xml"
    media_type = "application/xml"

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as XML and returns the resulting data.
        """
        parser_context = parser_context or {}
        encoding = parser_context.get("encoding", settings.DEFAULT_CHARSET)
        text = stream.body.decode(encoding)
        return text
