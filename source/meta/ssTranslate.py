import json
import locale
import os
from json.decoder import JSONDecodeError
from source.meta.common import common

class BabelFish():
    def __init__(self,subpath=["meta"],lang=None):
        localization_string = locale.getlocale()[0].lower() #get set localization
        self.locale = localization_string[:2] if lang is None else lang #let caller override localization
        self.langs = ["en"] #start with English
        if(not self.locale == "en"): #add localization
            self.langs.append(self.locale)
        self.lang_defns = {} #collect translations
        self.add_translation_file() #start with default translation file

    def add_translation_file(self,subpath=["meta"]):
        if not isinstance(subpath, list):
            subpath = [subpath]
        subpath.append("lang") #look in lang folder
        subpath = os.path.join(*subpath) #put in path separators
        for lang in self.langs:
            if lang not in self.lang_defns:
                self.lang_defns[lang] = {}
            langs_filename = common.get_resource(subpath,lang + ".json") #get filename of translation file
            if langs_filename and os.path.isfile(langs_filename): #if we've got a file
                with open(langs_filename,encoding="utf-8") as f: #open it
                    fJSON = {}
                    try:
                        fJSON = json.load(f)
                    except JSONDecodeError as e:
                        raise ValueError("Lang file malformed: " + langs_filename)
                    self.lang_defns[lang][subpath[:subpath.rfind(os.sep)].replace(os.sep,'.')] = fJSON #save translation definitions
            else:
                lang_path = subpath.replace(os.sep, '/') + f"/{lang}.json"
                print(f"🟡WARNING: Translation file: {lang_path} not found!")

    def translate(self, domain="", key="", subkey=""): #three levels of keys
        if os.sep in domain:
            domain = domain.replace(os.sep,'.')
        my_lang = self.lang_defns[self.locale] #handle for localization
        en_lang = self.lang_defns["en"] #handle for English
        if domain in my_lang and key in my_lang[domain] and subkey in my_lang[domain][key] and not my_lang[domain][key][subkey] == "": #get localization first
            display_text = my_lang[domain][key][subkey]
        elif domain in en_lang and key in en_lang[domain] and subkey in en_lang[domain][key] and not en_lang[domain][key][subkey] == "": #gracefully degrade to English
            display_text = en_lang[domain][key][subkey]
        else:
            # FIXME: English
            print("Can't Translate: ",domain,key,subkey)
            display_text = subkey.title() + ' ' + key #ungracefully degrade to requested keys
        return display_text
