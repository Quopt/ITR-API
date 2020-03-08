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

import logging
from logging.handlers import RotatingFileHandler
import sys
import os
import ITSRestAPISettings

# define all properties otherwise we will have cyclic dependencies on imports
log_formatter = logging.Formatter('ITR %(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
app_log = logging.getLogger('root')
log_file = 'ITR_API.log'
log_handler_backup_count = 10
filemode = 'a' if os.path.exists(log_file) else 'w'
ttylog = logging.StreamHandler(sys.stdout)
its_logging_initialised = False

def init(basepath):
    global log_handler_backup_count, ttylog, app_log, its_logging_initialised, filemode, log_file

    log_file = os.path.join(basepath, 'log', log_file)
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    try:
        log_handler_backup_count = ITSRestAPISettings.get_setting_for_customer("","LOG_HANDLER_BACKUP_COUNT",False,"")
    except:
        log_handler_backup_count = ""

    if log_handler_backup_count == "":
        log_handler_backup_count = 10
        ITSRestAPISettings.write_setting("","LOG_HANDLER_BACKUP_COUNT","10",True)
    else:
        log_handler_backup_count = int(log_handler_backup_count)

    log_handler = RotatingFileHandler(log_file, mode=filemode, maxBytes=5 * 1024 * 1024,
                                     backupCount=log_handler_backup_count, encoding=None, delay=0)
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)

    #ttylog = logging.StreamHandler(sys.stdout)
    ttylog.setLevel(logging.INFO)
    ttylog.setFormatter(log_formatter)

    #app_log = logging.getLogger('root')
    app_log.setLevel(logging.INFO)

    app_log.addHandler(log_handler)
    app_log.addHandler(ttylog)

    its_logging_initialised = True

def init_app_log(basepath):
    global its_logging_initialised
    if not its_logging_initialised:
        init(basepath)


