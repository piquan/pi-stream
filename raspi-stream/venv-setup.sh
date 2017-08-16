#! /bin/sh

# We need --system-site-packages to get RTIMULib, which isn't
# something you can just install with pip.
virtualenv --system-site-packages ENV
./ENV/bin/pip install httplib2 picamera sense_hat sdnotify pyserial
