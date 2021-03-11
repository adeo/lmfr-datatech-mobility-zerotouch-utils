import logging
import sys
import traceback
from flask import Flask, jsonify, request, Blueprint

from setupEnv import setupEnv

from src.zerotouch import getDevicesList, get_service, getConstructorsList, getDevicesListByConstructor, \
    getDevicesListByOrderId, applyConfigByNameToDevicesListByConstructor, applyConfigByNameToDevicesListByOrderId, \
    getOrderIdList

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
app = Flask(__name__)


@app.route('/')
def doc():
    return jsonify({
        "routes": [
            "/devices",
            "/devices/constructor/<constructor>",
            "/devices/order/<orderId>",
            "/constructor",
            "/configurations",
            "/devices/order/<orderId>/apply?config=XXXX",
            "/devices/constructor/<constructor>/apply?config=XXXX"
        ]}), 200


@app.route('/devices', methods=['GET'])
def devices():
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404

    customer_account = response['customers'][0]['name']
    devices = getDevicesList(service, customer_account)
    return jsonify({"Devices": devices, "Total": len(devices)}), 200


@app.route('/devices/constructor/<constructor>', methods=['GET'])
def devices_constructor(constructor=None):
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404

    customer_account = response['customers'][0]['name']
    devices = getDevicesListByConstructor(service, customer_account, None, constructor)
    return jsonify({"Devices": devices, "Total": len(devices)}), 200


@app.route('/devices/order/<orderId>', methods=['GET'])
def devices_order(orderId=None):
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404

    customer_account = response['customers'][0]['name']
    devices = getDevicesListByOrderId(service, customer_account, None, orderId)
    return jsonify({"Devices": devices, "Total": len(devices)}), 200


@app.route('/constructor', methods=['GET'])
def constructor():
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404

    customer_account = response['customers'][0]['name']
    return jsonify({
        'ConstructorsList': getConstructorsList(service=service, customer_account=customer_account)
    }), 200


@app.route('/order', methods=['GET'])
def order():
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404

    customer_account = response['customers'][0]['name']
    return jsonify({
        'ConstructorsList': getOrderIdList(service=service, customer_account=customer_account)
    }), 200


@app.route('/configurations', methods=['GET'])
def configurations():
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404

    customer_account = response['customers'][0]['name']
    return jsonify(
        response=service.customers().configurations().list(parent=customer_account).execute()["configurations"]), 200


@app.route('/devices/order/<orderId>/apply', methods=['GET'])
def apply_config_orderId(orderId=None):
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404
    customer_account = response['customers'][0]['name']
    applyConfigByNameToDevicesListByOrderId(service, customer_account, request.args.get('config'), orderId)
    return jsonify({"success": True}), 200


@app.route('/orange/<orderId>', methods=['GET'])
def orange(orderId=None):
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404
    customer_account = response['customers'][0]['name']
    devices = getDevicesListByOrderId(service, customer_account, None, orderId)
    if not devices:
        return jsonify({"success": False, "message": "la commande n'est pas presente dans la console"}), 404
    errors = applyConfigByNameToDevicesListByOrderId(service=service, customer_account=customer_account,
                                                     configName="WS1 - Prod - Managed", devicesList=devices,
                                                     orderId=orderId)
    if errors == 0:
        return jsonify({"success": True, "message": "OK", "devices": len(devices), "errors": errors}), 200
    else:
        return jsonify(
            {"success": True, "message": "Des erreurs sont survenues", "devices": len(devices), "errors": errors}), 404


@app.route('/devices/constructor/<constructor>/apply', methods=['GET'])
def apply_config_constructor(constructor=None):
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404
    customer_account = response['customers'][0]['name']
    applyConfigByNameToDevicesListByConstructor(service, customer_account, request.args.get('config'), constructor)
    return jsonify({"success": True}), 200


@app.route('/devices/constructor/<constructor>/unclaim', methods=['GET'])
def unclaim(constructor=None):
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404

    customer_account = response['customers'][0]['name']
    devices = getDevicesListByConstructor(service, customer_account, None, constructor)
    for device in devices:
        service.customers().devices().unclaim(parent=customer_account,
                                              body={
                                                  'device': {"deviceIdentifier": device["deviceIdentifier"]}}).execute()
    return jsonify({"success": True})


@app.route('/devices/unclaim/<imei>', methods=['GET'])
def unclaim_imei(imei=None):
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404

    customer_account = response['customers'][0]['name']
    result = service.customers().devices().unclaim(parent=customer_account,
                                                   body={
                                                       'device': {"deviceIdentifier": {"imei": imei,
                                                                                       'manufacturer': "oppo"}}}).execute()
    print(result)

    return jsonify({"success": "deviceId" in result.keys()})


if __name__ == "__main__":
    setupEnv()
    app.run(debug=True, host='0.0.0.0', port=8080)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
