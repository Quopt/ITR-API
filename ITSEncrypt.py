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

from cryptography.fernet import Fernet
import ITSRestAPISettings


def encrypt_string(toencrypt):
    key = ITSRestAPISettings.get_setting_for_customer("Master","EncryptionKey", False, "")

    if key == "":
        key = Fernet.generate_key()
        ITSRestAPISettings.write_setting("", "EncryptionKey", key.decode(), True)

    cipher_suite = Fernet(str.encode(key))
    return cipher_suite.encrypt(str.encode(toencrypt)).decode()


def decrypt_string(todecrypt):
    key = ITSRestAPISettings.get_setting_for_customer("Master", "EncryptionKey", False, "")

    if key == "":
        key = Fernet.generate_key()
        ITSRestAPISettings.write_setting("", "EncryptionKey", key.decode(), True)

    cipher_suite = Fernet(str.encode(key))
    return cipher_suite.decrypt(str.encode(todecrypt)).decode()
