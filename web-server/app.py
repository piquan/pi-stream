import sys
import json

with open("../key") as keyfile:
    KEY = keyfile.read().strip()

sensors = {'str': "{}",
           'type': "application/json"}

def app(env, start_response):
    if env['REQUEST_METHOD'] == 'PUT':
        if env['QUERY_STRING'] == KEY:
            sensors['str'] = env['wsgi.input'].read()
            sensors['type'] = env['CONTENT_TYPE']
            start_response('200 OK', [('Content-Type','text/plain'),
                                      ('Content-Length', '0')])
            return []
        else:
            start_response('401 Forbidden', [])
            return []
    elif env['REQUEST_METHOD'] == 'GET':
        start_response('200 OK', [('Content-Type', sensors['type'])])
        return [sensors['str']]
    else:
        start_response('405 Method Not Allowed', [])
        return []
