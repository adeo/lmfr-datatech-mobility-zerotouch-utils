import logging
import sys
import traceback
from flask import Flask, jsonify, request, Blueprint

from setupEnv import setupEnv

from src.zerotouch import getDevicesList, get_service, getConstructorsList, getDevicesListByConstructor, \
    getDevicesListByOrderId, applyConfigByNameToDevicesListByConstructor, applyConfigByNameToDevicesListByOrderId

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


@app.route('/devices/constructor/<constructor>/apply', methods=['GET'])
def apply_config_constructor(constructor=None):
    service = get_service()
    response = service.customers().list(pageSize=1).execute()
    if 'customers' not in response:
        return 'No zero-touch enrollment account found.', 404
    customer_account = response['customers'][0]['name']
    applyConfigByNameToDevicesListByConstructor(service, customer_account, request.args.get('config'), constructor)
    return jsonify({"success": True}), 200

if __name__ == "__main__":
    setupEnv()
    app.run(debug=True, host='0.0.0.0', port=8080)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
