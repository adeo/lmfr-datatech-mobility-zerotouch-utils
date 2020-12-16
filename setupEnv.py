import json
import os
import shutil
from os import path

from src.utils import getVaultCred


def setupEnv():
    """
    Va chercher le user_credential et le client_secret dans vault.
    :return:
    """
    if not path.exists("/tmp/client_secret.json"):
        vault_path = "zeroTouch/client_secret"
        data = getVaultCred(vault_path)
        with open('/tmp/client_secret.json', 'w') as json_file:
            json.dump(data, json_file)

    if not path.exists("/tmp/user_credential.json"):
        vault_path = "zeroTouch/user_credential"
        data = getVaultCred(vault_path)
        with open('/tmp/user_credential.json', 'w') as json_file:
            json.dump(data, json_file)
