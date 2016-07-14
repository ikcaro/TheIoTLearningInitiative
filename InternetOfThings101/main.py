#!/usr/bin/python

import paho.mqtt.client as paho
import json
import uuid
import psutil
import pywapi
import signal
import sys
import time
import dweepy

from threading import Thread
from flask import Flask
from flask_restful import Api, Resource

DeviceID = 0

class DataSensorRestApi(Resource):
    def get(self):
        netdata = psutil.net_io_counters()
        data = netdata.packets_sent + netdata.packets_recv
        return data

def functionDataActuator(status):
    print "Data Actuator Status %s" % status

def functionDataActuatorMqttOnMessage(mosq, obj, msg):
    print "Data Sensor Mqtt Subscribe Message!"
    functionDataActuator(msg.payload)

def functionDataActuatorMqttSubscribe():
    global DeviceID
    
    mqttclient = paho.Client()
    mqttclient.on_message = functionDataActuatorMqttOnMessage
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    mqttclient.subscribe("IoT101/" + DeviceID + "/DataActuator", 0)
    while mqttclient.loop() == 0:
        pass

def functionDataSensor():
    s = DataSensorRestApi()
    return s.get()

def functionDataSensorMqttOnPublish(mosq, obj, msg):
    print "Data Sensor Mqtt Published!"

def functionDataSensorMqttPublish():
    global DeviceID
    
    topic = "IoT101/" + DeviceID + "/DataSensor"
    mqttclient = paho.Client()
    mqttclient.on_publish = functionDataSensorMqttOnPublish
    mqttclient.connect("test.mosquitto.org", 1883, 60)
    while True:
        data = functionDataSensor()
        mqttclient.publish(topic, data)
        time.sleep(5)

def functionApiWeather():
    while True:
        data = pywapi.get_weather_from_weather_com('MXJO0043', 'metric')
        message = data['location']['name']
        message = message + ", Temperature " + data['current_conditions']['temperature'] + " C"
        message = message + ", Atmospheric Pressure " + data['current_conditions']['barometer']['reading'][:-3] + " mbar"
        
        print "API Weather: %s" % message
        time.sleep(5)

def functionServicesDweet():
    s = DataSensorRestApi()
    
    while True:
        dweepy.dweet_for('NetworkStatsIoT', {'Packets': s.get()})
        print dweepy.get_latest_dweet_for('NetworkStatsIoT')
        time.sleep(5)

def functionDataSensorMqttPublishIBM():
    global DeviceID
    
    organization = "quickstart"
    deviceType = "iotsample-gateway"
    topic = "iot-2/evt/status/fmt/json"
    username = ""
    password = ""
    
    clientID = "d:" + organization + ":" + deviceType + ":" + DeviceID
    broker = organization + ".messaging.internetofthings.ibmcloud.com"
    
    mqttclient = paho.Client(clientID)
    mqttclient.on_publish = functionDataSensorMqttOnPublish
    mqttclient.connect(broker, 1883, 60)
    
    while True:
        data = functionDataSensor()
        msg = json.JSONEncoder().encode({"d":{"netpackets":data}})
        mqttclient.publish(topic, msg)
        time.sleep(5)

def functionDataSensorFlask():
    app = Flask(__name__)
    api = Api(app)
    
    api.add_resource(DataSensorRestApi, '/sensor')
    app.run(host='0.0.0.0', debug=True)

def functionSignalHandler(signal, frame):
    sys.exit(0)

if __name__ == '__main__':
    DeviceID = hex(uuid.getnode())[2:-1]
    DeviceID = format(long(DeviceID, 16),'012x')
    
    print "Hello Internet of Things 101"
    print "Device ID: %s" % DeviceID

    signal.signal(signal.SIGINT,  functionSignalHandler)

    threadmqttpublish = Thread(target=functionDataSensorMqttPublish)
    threadmqttpublish.start()

    threadmqttsubscribe = Thread(target=functionDataActuatorMqttSubscribe)
    threadmqttsubscribe.start()
    
    threaddataweather = Thread(target=functionApiWeather)
    threaddataweather.start()
    
    threaddweet = Thread(target=functionServicesDweet)
    threaddweet.start()
    
    threadmqttpublishibm = Thread(target=functionDataSensorMqttPublishIBM)
    threadmqttpublishibm.start()

    functionDataSensorFlask()

# End of File
