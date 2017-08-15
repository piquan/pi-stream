#! /usr/bin/env python

import datetime
import json
import sys
import time

import httplib2
import picamera
import sense_hat
import serial

SERVER = sys.argv[1]

def volts_to_temp(vout):
    return vout * 100.0 - 50

http_conn = httplib2.Http()

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=0)
sense = sense_hat.SenseHat()
sense.clear()

with picamera.PiCamera() as camera:
    camera.resolution = (854, 480)
    camera.framerate = 30
    camera.awb_mode = 'sunlight'
    camera.drc_strength = 'high'
    camera.exposure_mode = 'auto'
    camera.hflip = True
    camera.vflip = True
    #camera.annotate_background = picamera.Color('black')
    camera.annotate_text = ""
    camera.annotate_text_size = 12
    camera.start_preview()
    camera.start_recording(sys.stdout, format='h264', bitrate=300000)
    temp_ext = None
    temp_ext_age = 1000
    upload_age = 1000
    while True:
        while ser.inWaiting():
            sensor_json = ser.readline()
            if not sensor_json:
                break
            try:
                sensor_volts = json.loads(sensor_json.decode('ascii'))
                temp_ext = volts_to_temp(sensor_volts['temp'])
                temp_ext_age = 0
            except:
                continue
        if temp_ext_age > 10:
            temp_ext_str = "Te:---"
        else:
            temp_ext_str = "%3.1fC" % (temp_ext,)
        temp_ext_age += 1

        time_str = datetime.datetime.now().strftime('%H:%M:%S')
        camera.annotate_text = ("%s Te:%s" % 
                                (time_str, temp_ext_str))

        if upload_age > 25:
            sensor_data = {"time": time.time(),
                           "tempext": temp_ext,
                           "temph": sense.get_temperature_from_humidity(),
                           "tempp": sense.get_temperature_from_pressure(),
                           "humidity": sense.get_humidity(),
                           "pressure": sense.get_pressure(),
                           "mag": sense.get_compass_raw(),
                           "gyro": sense.get_gyroscope_raw(),
                           "accel": sense.get_accelerometer_raw()
                          }
            sensor_json = json.dumps(sensor_data)
            (response, body) = http_conn.request(
                SERVER, "PUT",
                headers={'content-type':'application/json'},
                body=sensor_json)
            upload_age = 0
        upload_age += 1

        camera.wait_recording(0.2)

    camera.stop_recording()
