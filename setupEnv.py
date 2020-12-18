import json
import logging
from os import path
from src.utils import getVaultCred

gunicorn_logger = logging.getLogger('gunicorn.error')
logger = logging.getLogger(__name__)
logger.handlers = gunicorn_logger.handlers
logger.setLevel(gunicorn_logger.level)


def setupEnv():
    """
    Va chercher le user_credential et le client_secret dans vault.
    :return:
    """
    if not path.exists("/tmp/client_secret.json"):
        logger.info("vault: zeroTouch/client_secret start")
        try:
            vault_path = "zeroTouch/client_secret"
            data = getVaultCred(vault_path)
            with open('/tmp/client_secret.json', 'w') as json_file:
                json.dump(data, json_file)
        except Exception:
            logger.error("vault: zeroTouch/client_secret failed")

    if not path.exists("/tmp/user_credential.json"):
        logger.info("vault: zeroTouch/user_credential start")
        try:
            vault_path = "zeroTouch/user_credential"
            data = getVaultCred(vault_path)
            with open('/tmp/user_credential.json', 'w') as json_file:
                json.dump(data, json_file)
        except Exception:
            logger.error("vault: zeroTouch/user_credential failed")
