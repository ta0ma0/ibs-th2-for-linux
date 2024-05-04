#!/usr/bin/python3

import subprocess
import bluepy
import ruamel.yaml as yaml
from ruamel.yaml import YAML
import influxdb

sensors_config = 'sensors.yaml'

def load_config():
    with open(sensors_config) as f:
        yaml = YAML(typ='safe', pure=True)
        conf = yaml.load(f)
        return conf

def c2temp(char):
    val = int.from_bytes(char[0:2], 'little')
    if val >= 0xf000:
        val = -(0xffff - val + 1)

    return val / 100.0

def c2hum(char):
    return int.from_bytes(char[2:4], 'little') / 100.0

def b2bat(char):
    return int.from_bytes(char[0:2], 'little') / 100.0

def post_influxdb(client, mac, te, hu):
    body = [{
        'measurement': 'sensor',
        'fields': {'hu': hu, 'te': te,},
        'tags': {'address': mac},
    }]
    print(body)
    return client.write_points(body, time_precision='s')

def get_data(mac):
    temp_handle = 0x24
    device = bluepy.btle.Peripheral(mac)
    c = device.readCharacteristic(temp_handle)
    device.disconnect()
    return c2temp(c), c2hum(c)

def show_notification(mac, temperature):
    title = "Sensor Data"
    message = f"Outdoor - Temperature: {temperature} °C"
    subprocess.run(["notify-send", title, message])

if __name__ == '__main__':
    conf = load_config()
    for sensor in conf:
        mac = sensor['mac']
        try:
            temperature, humidity = get_data(mac)
            # print(f"Outdoor - Temperature: {temperature}")
            print(temperature)
            # show_notification(mac, temperature)
        except Exception as e:
            print(f"Error retrieving data from sensor {mac}: {e}")

