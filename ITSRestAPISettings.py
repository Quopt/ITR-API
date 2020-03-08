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

# helper module to manage settings
import os
import ITSRestAPIDB
import ITSRestAPIORMExtensions
from sqlalchemy.orm import sessionmaker
import json
import ITSHelpers

settings_loaded = False
settings_cache = {}

def get_setting(setting_name, defaultval = ""):
    global settings_loaded
    import application

    if not settings_loaded:
        application.app.config.from_pyfile('application.cfg')
        settings_loaded = True

    try:
        # support setting of ANY parameter as command line parameter override on docker
        if os.environ[setting_name]:
            return os.environ[setting_name]
        else:
            return defaultval
    except:
        try:
            return application.app.config[setting_name]
        except:
            return ""

def write_setting(customer_id, setting_name, setting_value, par_protected):
    with ITSRestAPIDB.session_scope(customer_id) as session:
        param = session.query(ITSRestAPIORMExtensions.SystemParam).filter(
            ITSRestAPIORMExtensions.SystemParam.ParameterName == setting_name).first()
        if param is None:
            param = ITSRestAPIORMExtensions.SystemParam()
            param.ParameterName = setting_name
            param.ParValue = setting_value
            param.ParProtected = par_protected
            session.add(param)
        else:
            param.ParValue = setting_value

def get_setting_for_customer(customer_id, setting_name, check_master_db_too, consultant_id):
    global settings_cache

    setting_value = get_setting(setting_name)

    if customer_id == "":
        customer_id = "Master"

    with ITSRestAPIDB.session_scope(customer_id) as session:
        with ITSRestAPIDB.session_scope("") as masterSession:
            param = None
            if consultant_id != "" and customer_id != "Master":
                try:
                    # check cache
                    if settings_cache[consultant_id] :
                        plugin_data = settings_cache[consultant_id]
                    else:
                        #retrieve settings and place in cache
                        consultant = session.query(ITSRestAPIORMExtensions.SecurityUser).filter(
                            ITSRestAPIORMExtensions.SecurityUser.ID == consultant_id).first
                        if consultant.PluginData.strip() != "":
                            plugin_data = json.loads(consultant.PluginData)
                            settings_cache[consultant_id] = plugin_data
                        else:
                            settings_cache[consultant_id] = ""
                            #check if setting found and then use that

                    if plugin_data['settings'][setting_name].strip() != "":
                        param = ITSHelpers.Empty()
                        param.ParValue = plugin_data['settings'][setting_name]
                except:
                    pass

            if param is None or param.ParValue == "":
                param = session.query(ITSRestAPIORMExtensions.SystemParam).filter(
                    ITSRestAPIORMExtensions.SystemParam.ParameterName == setting_name).first()

            if param is None or param.ParValue == "":
                if check_master_db_too and customer_id != "Master":
                    param = masterSession.query(ITSRestAPIORMExtensions.SystemParam).filter(
                           ITSRestAPIORMExtensions.SystemParam.ParameterName == setting_name).first()

            if param is None or param.ParValue == "":
                return setting_value
            else:
                return param.ParValue

