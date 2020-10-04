# Copyright 2019 by Quopt IT Services BV
#
#  Licensed under the Artistic License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    https://raw.githubusercontent.com/Quopt/ITR-webclient/master/LICENSE
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import http.client, urllib.parse, ITSRestAPISettings
import json, uuid
import ssl
from ITSLogging import *

host = 'api.cognitive.microsofttranslator.com'
path = '/translate'


# source language is always english in this case
def get_translation(target_language, text_to_translate):
    app_log.info('Requesting translation %s :  %s', target_language, text_to_translate)
    translation = get_translation_with_source_language("en", target_language, text_to_translate)
    app_log.info(">>> %s ", translation)
    return translation

def get_translation_if_needed(target_language, translation_key, text_to_translate, existing_translations):
    try:
        if existing_translations[translation_key]:
            return existing_translations[translation_key]['value'], False
    except:
        return get_translation(target_language, text_to_translate), True

def get_translation_if_needed_from_file(target_language, translation_key, text_to_translate, app_instance_path, write_when_missing):
    filename = os.path.join(app_instance_path, 'translations/', target_language + '.json')
    current_translation = json.load(open(filename, 'r'))
    try:
        translation_found = current_translation[translation_key]['value']
    except:
        translation_found = text_to_translate
        if write_when_missing:
            current_translation[translation_key] = {}
            current_translation[translation_key]['value'] = get_translation(target_language, translation_found)
            try:
                with open(filename, 'w') as translationFile:
                    translationFile.write(json.dumps(current_translation, indent=1, sort_keys=True))
                    translationFile.close()
            except:
                pass

    return translation_found

def translation_available():
    return ITSRestAPISettings.get_setting_for_customer("",'TRANSLATE_AZURE_KEY', False, "") != ""

def get_translation_with_source_language(source_language, target_language, text_to_translate):
    if len(text_to_translate) < 5000:
        return get_translation_with_source_language_part(source_language, target_language, text_to_translate)
    else:
        return text_to_translate # texts longer than 5000 characters cannot be translated

def get_translation_with_source_language_part(source_language, target_language, text_to_translate):
    # Replace the subscriptionKey string value with your valid subscription key in the application.cfg file or environment variable TRANSLATE_AZURE_KEY
    subscriptionKey = ITSRestAPISettings.get_setting_for_customer("",'TRANSLATE_AZURE_KEY', False, "")

    if subscriptionKey != "":
        params = '?api-version=3.0&textType=html&from=' + source_language + '&to=' + target_language
        headers = {"Ocp-Apim-Subscription-Key": str(subscriptionKey),
                   "Content-Type":"application/json",
                   "X-ClientTraceId": str(uuid.uuid4())}
        try:
         tempbody = {}
         tempbody["Text"] = text_to_translate
         body = '['+ json.dumps(tempbody) + ']' 
         #body = ('[{"Text": "%s"}]' % str(text_to_translate).replace('"','\"'))
         conn = http.client.HTTPSConnection(host, context = ssl._create_unverified_context())
         conn.request("POST", path + params, body, headers)
         response = conn.getresponse()
         json_string = response.read()
         root = json.loads(json_string)

         return root[0]['translations'][0]['text']
        except Exception as e:
            app_log.error("%s", e)
            return None
    else:
        return None
