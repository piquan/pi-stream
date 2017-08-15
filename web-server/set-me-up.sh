#! /bin/sh

set +ex
virtualenv ENV
ENV/bin/pip install uwsgi
