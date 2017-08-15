./ENV/bin/uwsgi --single --strict --manage-script-name --wsgi-file=app.py --callable=app --harakiri=5 --py-autoreload=1 --socket=/tmp/pi-stream.sock --chmod-socket=1
