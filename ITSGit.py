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

import os, time
import subprocess
import json

def clone_or_refresh_repo(instance_path, repo_url):
    # https://github.com/Quopt/ITR-Docker
    short_repo_name = repo_url.split('/')[-1]
    basepathname = os.path.join(os.sep, instance_path, 'cache', 'git')
    pathname = os.path.join(os.sep, instance_path, 'cache', 'git', short_repo_name)
    if not os.path.exists(basepathname):
        os.makedirs(basepathname)
    if not os.path.exists(pathname):
        os.makedirs(pathname)
    if not os.path.exists(pathname):
        subprocess.run(['git','clone',repo_url], cwd=basepathname)
    else:
        subprocess.run(['git', 'reset', '--hard', 'origin/master'], cwd=pathname)

def list_repo_files(instance_path, repo_url):
    short_repo_name = repo_url.split('/')[-1]
    pathname = os.path.join(os.sep, instance_path, 'cache', 'git', short_repo_name)

    returnlist = []
    onlyfiles = [f for f in os.listdir(pathname) if os.path.isfile(os.path.join(pathname, f))]
    for f in onlyfiles:
        if f != "LICENSE" and f != "README.md" and f.split('.')[-1] != "itrinfo":
            a = {}
            a['name'] = f
            a['getdate'] = time.ctime(os.path.getmtime(os.path.join(pathname, f)))
            a['explanation'] = ''
            tempfilename = os.path.join(pathname, f + '.itrinfo')
            if os.path.exists(tempfilename):
                a['explanation'] = open(tempfilename,"r").read()

            returnlist.append(a)

    return json.dumps(returnlist)


