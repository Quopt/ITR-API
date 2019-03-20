# Copyright 2019 by Quopt IT Services BV
#
#  Licensed under the Artistic License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    https://opensource.org/licenses/Artistic-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import http.client, urllib.parse, ITSRestAPISettings
import json, uuid
from ITSLogging import *

#host = 'api.microsofttranslator.com'
#path = '/V2/Http.svc/Translate'
host = 'api.cognitive.microsofttranslator.com'
path = '/translate'


# source language is always english in this case
def get_translation(target_language, text_to_translate):
    app_log.info('Requesting translation %s :  %s', target_language, text_to_translate)
    translation = get_translation_with_source_language("en", target_language, text_to_translate)
    app_log.info(">>> %s ", translation)
    return translation

def translation_available():
    return ITSRestAPISettings.get_setting_for_customer("",'TRANSLATE_AZURE_KEY', False, "") != ""

def get_translation_with_source_language(source_language, target_language, text_to_translate):
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
         conn = http.client.HTTPSConnection(host)
         conn.request("POST", path + params, body, headers)
         response = conn.getresponse()
         json_string = response.read()
         root = json.loads(json_string)

         return root[0]['translations'][0]['text']
        except:
         return None
    else:
        return None
