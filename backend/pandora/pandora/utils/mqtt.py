# -*- coding: utf-8 -*-
import paho.mqtt.publish as pub
import paho.mqtt.subscribe as sub
import paho.mqtt.client as mqtt

import logging
import os
import json

import msgpack

LOG = logging.getLogger(__name__)
MQTT_HOST = os.environ.get('MQTT_HOST', "10.88.188.226")
MQTT_PORT = int(os.environ.get('MQTT_PORT', 13125))
client_pub_id = "publish_pandora_pub{}".format(os.environ.get('MQTT_CLIENT', "idaas"))
client_sub_id = "publish_pandora_sub{}".format(os.environ.get('MQTT_CLIENT', "idaas"))
username = os.environ.get('MQTT_USER', "mtpub")
password = os.environ.get('MQTT_PASSWORD', "G67*@99XfjJ3")
message_type = "idaas"


def _on_publish(client, userdata, mid):
    LOG.info("on publish:{}".format(mid))


def dumps_message(message):
    sn = message.pop("member", None)
    data = {
        "type": message_type,
        "sn": sn,
        "data": message
    }
    LOG.info(data)
    return json.dumps(data)


def loads_message(message):
    return json.loads(message)


def publish(topic, message):
    return pub.single(topic, payload=dumps_message(message),
                      hostname=MQTT_HOST, port=MQTT_PORT,
                      client_id=client_pub_id, keepalive=3600,
                      auth={'username': username, 'password': password})


def subscribe(topic, msg_count=2):
    message = sub.simple(topic, msg_count=msg_count,
                         hostname=MQTT_HOST, port=MQTT_PORT,
                         client_id=client_sub_id, keepalive=3600,
                         auth={'username': username, 'password': password}, clean_session=False)
    return loads_message(message.payload)


class MqttPublish(object):
    def __init__(self, keepalive=60, clean_session=False, protocol=mqtt.MQTTv311, transport="tcp"):
        self.mqtt_params = {
            "keepalive": keepalive,
            "clean_session": clean_session,
            "protocol": protocol,
            "transport": transport,
            "client_id": client_pub_id,
            "username": username,
            "password": password,
            "host": MQTT_HOST,
            "port": MQTT_PORT
        }
        self.client = self.init_client()

    def init_client(self):
        client = mqtt.Client(client_id=self.mqtt_params["client_id"], clean_session=self.mqtt_params["clean_session"],
                             protocol=self.mqtt_params["protocol"],
                             transport=self.mqtt_params["transport"])
        client.on_publish = _on_publish
        client.username_pw_set(self.mqtt_params["username"], self.mqtt_params["password"])
        client.connect(self.mqtt_params["host"], self.mqtt_params["port"], self.mqtt_params["keepalive"])
        client.loop_start()
        return client

    def __getattr__(self, attr):
        if attr not in self.__dict__:
            return getattr(self.client, attr)
        return self.__dict__[attr]

    def publish(self, topic, message, qos=0, retain=False):
        # if self._state != mqtt.mqtt_cs_connected:
        #     self.disconnect()
        #     LOG.info("close old client:{}".format(self.client))
        #     self.client = self.init_client()
        payload = dumps_message(message)
        LOG.info("topic: {} -- {}".format(topic, payload))
        return self.client.publish(topic, payload, qos=qos, retain=retain)
