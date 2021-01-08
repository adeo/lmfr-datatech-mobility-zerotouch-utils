import logging
import sys
from apiclient import discovery
import httplib2
from oauth2client import tools
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import json

# https://github.com/googleapis/google-api-python-client/issues/299
logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)

SCOPES = ['https://www.googleapis.com/auth/androidworkzerotouchemm']
# credential stored in gcp section google api
CLIENT_SECRET_FILE = '/tmp/client_secret.json'
# generate after calling get_credential
USER_CREDENTIAL_FILE = '/tmp/user_credential.json'


def get_credential():
    """
    Creates a Credential object with the correct OAuth2 authorization.

    Ask the user to authorize the request using their Google Account in their
    browser. Because this method stores the credential in the
    USER_CREDENTIAL_FILE, the user is typically only asked to the first time they
    run the script.

    :return: credential, User credential
    :rtype: credential
    """
    flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    storage = Storage(USER_CREDENTIAL_FILE)
    credential = storage.get()

    if not credential or credential.invalid:
        credential = tools.run_flow(flow, storage)  # skipping flags for brevity
    return credential


def get_service():
    """
    Creates a service endpoint for the zero-touch enrollment API.

    Builds and returns an authorized API client service for v1 of the API. Use
    the service endpoint to call the API methods.

    :return: A service Resource object with methods for interacting with the service.
    """
    http_auth = get_credential().authorize(httplib2.Http())
    return discovery.build('androiddeviceprovisioning', 'v1', http=http_auth)


def getConfigByName(service=None, customer_account=None, name=None):
    """
    Get config with the name name
    google docs for configuration: https://developers.google.com/zero-touch/reference/customer/rest/v1/customers.configurations

    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment
    :param str name: name of configuration

    :return: configuration
    :rtype: dict
    """
    response = service.customers().configurations().list(parent=customer_account).execute()
    for configuration in response["configurations"]:
        if name.lower() == configuration["configurationName"].lower():
            return configuration
    return {}


def getDevicesList(service, customer_account):
    """
    Get all devices in zero touch console
    google deocs for devices: https://developers.google.com/zero-touch/reference/customer/rest/v1/customers.devices

    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment

    :return: list Devices
    :rtype: list Device
    """
    pageToken = ""
    listDevices = list()
    nbr = 0
    while pageToken is not None:
        response = service.customers().devices().list(parent=customer_account, pageSize=100,
                                                      pageToken=pageToken).execute()
        for devices in response["devices"]:
            if "imei" in devices['deviceIdentifier'] and "manufacturer" in devices['deviceIdentifier']:
                listDevices.append({
                    "name": devices['name'],
                    "imei": devices['deviceIdentifier']['imei'],
                    "manufacturer": devices['deviceIdentifier']['manufacturer'],
                    "deviceId": devices["deviceId"],
                    "orderId": devices["deviceMetadata"]["entries"][
                        "ordernumber"] if "deviceMetadata" in devices and "entries" in devices["deviceMetadata"] and
                                          devices["deviceMetadata"]["entries"]["ordernumber"] else None,
                    "deviceIdentifier": devices["deviceIdentifier"],
                    "configuration": devices["configuration"] if "configuration" in devices else None
                })
            else:
                pass
        if "nextPageToken" in response:
            pageToken = response["nextPageToken"]
        else:
            pageToken = None
    print(f"nbr: {nbr}")
    return listDevices


def getModelList(service=None, customer_account=None):
    """
    Useless fonction.
    check models allowed here: https://developers.google.com/zero-touch/resources/manufacturer-names#model-names
    Get all models.
    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment

    :return: dict of all models
    :rtype: dict
    """
    devicesList = getDevicesList(service=service, customer_account=customer_account)
    modelsDict = dict()
    modelsDict["noModel"] = 0
    for device in devicesList:
        if "model" in device["deviceIdentifier"]:
            if device["deviceIdentifier"]["model"].lower() not in modelsDict.keys():
                modelsDict[device["manufacturer"].lower()] = 1
            else:
                modelsDict[device["manufacturer"].lower()] += 1
        else:
            modelsDict["noModel"] += 1
    return modelsDict


def getConstructorsList(service=None, customer_account=None):
    """
    Get all constructors.\n
    check docs for manufacurer value.\n
    here: https://developers.google.com/zero-touch/resources/manufacturer-names#manufacturers-names
    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment

    :return: list of all constructors
    :rtype: list
    """
    devicesList = getDevicesList(service=service, customer_account=customer_account)
    constructorList = list()
    for device in devicesList:
        if device["manufacturer"].lower() not in constructorList:
            constructorList.append(device["manufacturer"].lower())
    return constructorList


def getOrderIdList(service=None, customer_account=None, devicesList=None):
    """
    Get all constructors.\n
    check docs for manufacturer value.\n
    here: https://developers.google.com/zero-touch/resources/manufacturer-names#manufacturers-names
    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment

    :return: list of all constructors
    :rtype: list
    """
    if devicesList is None:
        devicesList = getDevicesList(service=service, customer_account=customer_account)
    orderIdList = list()
    for device in devicesList:
        if device["orderId"] is not None and device["orderId"].lower() not in orderIdList:
            orderIdList.append(device["orderId"].lower())
    return orderIdList


def getDevicesListByConstructor(service=None, customer_account=None, devicesList=None, constructor=None):
    """
    Get devices List by Constructor.\n
    If devicesList is None getDevicesList() is assigned.

    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment
    :param list devicesList: devices List
    :param str constructor: constructor name

    :return: list of devices with constructor name constructor.
    :rtype: list
    """
    if devicesList is None:
        devicesList = getDevicesList(service, customer_account)
    return [device for device in devicesList if constructor.lower() == device["manufacturer"].lower()]


def getDevicesListByOrderId(service=None, customer_account=None, devicesList=None, orderId=None):
    """
    Get devices List by OrderId.\n
    If devicesList is None getDevicesList() is assigned.

    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment
    :param list devicesList: devices List
    :param str orderId: orderId

    :return: list of devices with orderId ordierId.
    :rtype: list
    """
    if devicesList is None:
        devicesList = getDevicesList(service, customer_account)
    return [device for device in devicesList if
            "orderId" in device and device["orderId"] is not None and orderId.lower() == device["orderId"].lower()]


def getDevicesListByConfig(service=None, customer_account=None, devicesList=None, name=None):
    """
    Get devices List by Constructor.\n
    If devicesList is None getDevicesList() is assigned.

    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment
    :param list devicesList: devices List
    :param str constructor: constructor name

    :return: list of devices with constructor name constructor.
    :rtype: list
    """
    config = getConfigByName(service, customer_account, name)
    if devicesList is None:
        devicesList = getDevicesList(service, customer_account)
    return [device for device in devicesList if
            "configuration" in device and device["configuration"] is not None and config["name"] == device[
                "configuration"].lower()]


def verifyConfig(service=None, customer_account=None, devicesList=None, configName=None):
    """
    Check if all devices in devicesList is in good configuration. \n
    If devicesList is None getDevicesList() is assigned.\n
    True if all devices is in a good configuration, False else

    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment
    :param list devicesList: devices List
    :param str configName: name of configuration(pattern: customers/[CUSTOMER_ID]/configurations/[CONFIGURATION_ID])

    :return: check config
    :rtype: bool
    """
    if devicesList is None:
        devicesList = getDevicesList(service, customer_account)
    counter = 0
    for device in devicesList:
        if configName == device["configuration"]:
            counter += 1
    return counter == len(devicesList)


def applyConfigDevices(service=None, customer_account=None, devicesList=None, configuration=None):
    """
    Apply one configuration to devices list
    If devicesList is None getDevicesList() is assigned.
    google docs for configuration: https://developers.google.com/zero-touch/reference/customer/rest/v1/customers.configurations

    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment
    :param list devicesList: devices List
    :param dict configuration: configuration

    :return: number of errors
    :rtype: int
    """
    if devicesList is None:
        devicesList = getDevicesList(service, customer_account)

    errors = 0
    for device in devicesList:
        deviceReference = {"deviceId": device["deviceId"]}
        response = service.customers().devices().applyConfiguration(
            parent=customer_account,
            body={"device": deviceReference, "configuration": configuration["name"]}
        ).execute()
        if response != {}:
            errors += 1
    return errors


def applyConfigByNameToDevicesListByConstructor(service=None, customer_account=None, configName=None, constructor=None):
    """
    Apply config with name configName to all devices with constructor constructor.

    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment
    :param str constructor: constructor name
    :param str configName: configurationName (zero-touch enrollment portal displays this name)

    :return: number of errors
    :rtype: int
    """
    devicesList = getDevicesListByConstructor(service=service, customer_account=customer_account,
                                              constructor=constructor)
    config = getConfigByName(service=service, customer_account=customer_account, name=configName)
    return applyConfigDevices(service=service, customer_account=customer_account, devicesList=devicesList,
                              configuration=config)


def applyConfigByNameToDevicesListByOrderId(service=None, customer_account=None, configName=None, devicesList=None, orderId=None):
    """
    Apply config with name configName to all devices with orderid.

    :param devicesList:
    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment
    :param str OrderId: orderId
    :param str configName: configurationName (zero-touch enrollment portal displays this name)

    :return: number of errors
    :rtype: int
    """
    if devicesList is None:
        devicesList = getDevicesListByOrderId(service=service, customer_account=customer_account,
                                              orderId=orderId)
    config = getConfigByName(service=service, customer_account=customer_account, name=configName)
    return applyConfigDevices(service=service, customer_account=customer_account, devicesList=devicesList,
                              configuration=config)


def removeConfiguration(service=None, customer_account=None, devicesList=None):
    """
    Remove configuration to devices list
    If devicesList is None getDevicesList() is assigned.
    google docs for configuration: https://developers.google.com/zero-touch/reference/customer/rest/v1/customers.configurations

    :param Resource service: service resource
    :param str customer_account: name of customer account needed to access google api zero touch enrollment
    :param list devicesList: devices List

    :return: number of errors
    :rtype: int
    """
    if devicesList is None:
        devicesList = getDevicesList(service, customer_account)

    errors = 0
    for device in devicesList:
        deviceReference = {"deviceId": device["deviceId"]}
        response = service.customers().devices().removeConfiguration(
            parent=customer_account,
            body={"device": deviceReference}
        ).execute()
        if response != {}:
            errors += 1
    return errors
