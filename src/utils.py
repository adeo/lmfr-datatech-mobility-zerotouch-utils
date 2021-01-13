import requests


def getVaultCred(path):
    """
    Va chercher les creds sur vault.
    :param path: le chemin de la creds
    :return: le json vault
    """
    vault_url = "https://vault.factory.adeo.cloud"
    # nom du repo sur le vault-module editor
    gcp_role = "zero-touch-prod"
    vault_namespace = "frlm/mobilitytech"
    headers = {
        'Metadata-Flavor': "Google"
    }
    # google token
    response = requests.get(
        "http://metadata/computeMetadata/v1/instance/service-accounts/default/identity?audience=https://vault.factory.adeo.cloud/vault/" + gcp_role + "&format=full",
        headers=headers, verify=False)
    google_token = response.text

    # get le token de login de vault
    headers = {
        "X-Vault-Namespace": vault_namespace
    }
    response = requests.post(vault_url + '/v1/auth/gcp/login', json={"role": gcp_role, "jwt": google_token},
                             headers=headers)
    login_obj = response.json()
    vault_token = login_obj["auth"]["client_token"]
    # call pour get les creds
    headers = {
        "X-Vault-Token": vault_token,
        "X-Vault-Namespace": vault_namespace
    }
    vault_secret = path
    response = requests.get(vault_url + '/v1/secret/data/' + vault_secret, headers=headers)
    return response.json()["data"]["data"]


