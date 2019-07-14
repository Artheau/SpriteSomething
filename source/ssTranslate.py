import json
import locale
import os
from source import common

def translate(key = "", subkey = "", subpath = ""):
  localization_string = locale.getdefaultlocale()[0]           #e.g. "en_US"
  language_code = localization_string[:2]   #grab just the two letters that give the language
  langs_filename = common.get_resource(language_code + ".json",os.path.join(subpath,"lang"))
  default_langs_filename = common.get_resource("en.json",os.path.join(subpath,"lang"))

  #TODO: load the JSON file as a static variable, so that these files are only loaded once
  with open(default_langs_filename,encoding="utf-8") as f:
    default_langs = json.load(f)
  if langs_filename:  #filename may be None, if this localization is not available
    with open(langs_filename,encoding="utf-8") as f:
      langs = json.load(f)
  else:
    langs = default_langs

  if key in langs and subkey in langs[key]:
    display_text = langs[key][subkey]
  elif key in default_langs and subkey in default_langs[key]:
    display_text = default_langs[key][subkey]
  else:
    display_text = subkey.title() + ' ' + key
  return display_text
