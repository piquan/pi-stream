#! /usr/bin/env python

import datetime
import json
import sys
import time

import httplib2
import picamera
import sdnotify
import sense_hat
import serial

SERVER = sys.argv[1]

def volts_to_temp(vout):
    return vout * 100.0 - 50.0

def ctof(c):
    return c * 9.0 / 5.0 + 32.0

notifier = sdnotify.SystemdNotifier()
http_conn = httplib2.Http(timeout=1)
http_conn.force_exception_to_status_code = True
last_http_status = None
response_status_age = 0

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=0)
sense = sense_hat.SenseHat()
sense.clear()

with picamera.PiCamera() as camera:
    camera.resolution = (854, 480)
    camera.framerate = 30
    camera.awb_mode = 'sunlight'
    camera.drc_strength = 'high'
    camera.exposure_mode = 'auto'
    camera.rotation = 90
    #camera.hflip = True
    #camera.vflip = True
    #camera.annotate_background = picamera.Color('black')
    camera.annotate_text = ""
    camera.annotate_text_size = 12
    camera.start_preview(alpha=200)
    camera.start_recording(sys.stdout, format='h264', bitrate=200000,
                           intra_period=60)
    temp_ext = None
    temp_ext_age = 1000
    upload_age = 1000
    try:
        with open("input-logs.json", "a") as log_fh:
            notifier.notify("READY=1")
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
                    temph = sense.get_temperature_from_humidity()
                    tempp = sense.get_temperature_from_pressure()
                    awb_gains = camera.awb_gains
                    sensor_data = {"time": time.time(),
                                   "sensor": {
                                       "tempext": temp_ext,
                                       "temph": temph,
                                       "tempp": tempp,
                                       "tempextf": ctof(temp_ext),
                                       "temphf": ctof(temph),
                                       "temppf": ctof(tempp),
                                       "humidity": sense.get_humidity(),
                                       "pressure": sense.get_pressure(),
                                       "mag": sense.get_compass_raw(),
                                       "gyro": sense.get_gyroscope_raw(),
                                       "accel": sense.get_accelerometer_raw(),
                                   },
                                   "camera": {
                                       "analoggain": float(camera.analog_gain),
                                       "awbgains": {"r": float(awb_gains[0]),
                                                    "b": float(awb_gains[1])},
                                       "brightness": camera.brightness,
                                       "contrast": camera.contrast,
                                       "digitalgain":
                                           float(camera.digital_gain),
                                       "exposurecompensation":
                                           camera.exposure_compensation,
                                       "exposurespeed": camera.exposure_speed,
                                       "iso": camera.iso,
                                       "saturation": camera.saturation,
                                       "sharpness": camera.sharpness,
                                  }
                                 }
                    sensor_json = json.dumps(sensor_data)
                    log_fh.write(sensor_json + "\n")
                    log_fh.flush()
                    (response, body) = http_conn.request(
                        SERVER, "PUT",
                        headers={'content-type':'application/json'},
                        body=sensor_json)
                    if response.status != last_http_status or \
                       response.status != '200' and response_status_age > 100:
                        errmsg = "\n*** HTTP: " + str(response) + "\n"
                        if (len(body) < 256):
                            errmsg += body + "\n"
                        sys.stderr.write(errmsg)
                        last_http_status = response.status
                        response_status_age = 0
                    response_status_age += 1
                    upload_age = 0
                    notifier.notify("STATUS=Frame %i, HTTP %i, Temp %iC" %
                                    (camera.frame.index, response.status,
                                     temp_ext))
                upload_age += 1

                camera.wait_recording(0.2)
                notifier.notify("WATCHDOG=1")

    finally:
        notifier.notify("STOPPING=1")
        camera.stop_preview()
        camera.stop_recording()
