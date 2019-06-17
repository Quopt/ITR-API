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
