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

import datetime

global_cache = {}
global_cache_timekey = ""


def check_in_cache(key):
    global global_cache, global_cache_timekey
    now = datetime.datetime.now()
    if global_cache_timekey != now.strftime("%H:00") or global_cache_timekey == "":
        # clear the cache every hour completely
        global_cache = {}
        global_cache_timekey = now.strftime("%H:00")

        return None
    else:
        timeout = global_cache.get('timeout.' + key)
        if timeout is not None:
            if timeout < now:
                return None
        return global_cache.get(key)


def add_to_cache(key, value):
    global global_cache

    global_cache[key] = value
    global_cache['timeout.' + key] = datetime.datetime.now() + datetime.timedelta(minutes=1)  # 1 min default timeout


def add_to_cache_with_timeout(key, timeout, value):
    global global_cache

    timeoutcalc = datetime.datetime.now() + datetime.timedelta(minutes=timeout)
    global_cache[key] = value
    global_cache['timeout.' + key] = timeoutcalc

def reset_cache():
    global global_cache
    global_cache = {}
