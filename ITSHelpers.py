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

import string
import os, sys, psutil
import shutil
from dirsync import sync
from ITSLogging import app_log

def string_split_to_filepath(string_to_split):
    string_to_split = to_filepath(string_to_split)
    new_string = ""
    x = 0
    while x < len(string_to_split):
        new_string = new_string + string_to_split[x:x+2] + os.sep
        x = x + 2
    return new_string

def to_filename(filename):
    valid_chars = "%s%s." % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in filename if c in valid_chars).lower()
    return filename

def to_filepath(filepath):
    valid_chars = "%s%s" % (string.ascii_letters, string.digits)
    filepath = ''.join(c for c in filepath if c in valid_chars).upper()
    return filepath

def elements_in_folder(filepath):
    list = os.listdir(filepath)
    return len(list)

def remove_folder(filepath, basepathname = ""):
    shutil.rmtree(filepath, ignore_errors=True)
    filepath, tail = os.path.split(filepath)

    if basepathname != "" :
        while elements_in_folder(filepath) == 0 and filepath != basepathname:
            shutil.rmtree(filepath, ignore_errors=True)
            filepath, tail = os.path.split(filepath)

def copy_folder(filepath_src, filepath_dst):
    for item in os.listdir(filepath_src):
        s = os.path.join(filepath_src, item)
        d = os.path.join(filepath_dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

def copy_folder_excluding_dot_folders(filepath_src, filepath_dst):
    for item in os.listdir(filepath_src):
        s = os.path.join(filepath_src, item)
        d = os.path.join(filepath_dst, item)
        lastfolder = os.path.basename(d)
        if os.path.isdir(s):
            if lastfolder[:1] != "." and lastfolder != "instance":
                app_log.info("Check folder for changed files from " + s + " to " + d)
                try:
                    copy_folder_excluding_dot_folders(s, d)
                except:
                    app_log.info("Check folder failed.")
        else:
            if os.path.getmtime(s) != os.path.getmtime(d):
              app_log.info("Copy file from " + s + " to " + d)
              try:
                  shutil.copyfile(s, d)
              except:
                  app_log.info("Copy file from " + s + " to " + d + " failed.")


def list_folder(filepath):
    a = []
    for root, dirs, files in os.walk(filepath):
        for f in files:
            a.append( f )
#            a.append({'type': os.path.basename(root), 'filename': f})
    return a

class Empty:
    pass

def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """

    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except:
        e = sys.exc_info()[0]
        #app_log.error(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)

