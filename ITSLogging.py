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

import logging
from logging.handlers import RotatingFileHandler
import sys
import os

log_formatter = logging.Formatter('ITR %(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

logFile = 'instance/log/ITR_API.log';

if not os.path.exists(os.path.dirname(logFile)):
    os.makedirs(os.path.dirname(logFile))

filemode = 'a' if os.path.exists(logFile) else 'w'

my_handler = RotatingFileHandler(logFile, mode=filemode, maxBytes=5 * 1024 * 1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

ttylog = logging.StreamHandler(sys.stdout)
ttylog.setLevel(logging.INFO)
ttylog.setFormatter(log_formatter)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)

app_log.addHandler(my_handler)
app_log.addHandler(ttylog)


