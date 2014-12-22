#!/usr/bin/env python

from flask import Flask, make_response, render_template, request, send_from_directory, url_for
from flask.views import MethodView
import simplejson as json
import subprocess
import logging
import os

from ddm import DeviceDisplayMatrix

app = Flask(__name__)
registry = dict()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/<template_name>')
@app.route('/', defaults={'template_name': 'index.html'})
def direct_to_template(template_name, **kwargs):
    return render_template(template_name, **kwargs)


def json_response(obj, response=200, headers=None):
    if headers is None:
        headers = dict()
    headers['Content-Type'] = 'application/json'
    if len(obj) == 0:
        text = "[]"
    else:
        text = json.dumps(obj, indent=4, sort_keys=True)
    return text, response, headers


class RegistryAPI(MethodView):

    def get(self, name, key):
        if name is None:
            return json_response(registry)

        try:
            index = registry[name]
        except KeyError:
            index = registry.setdefault(name, dict())
            return json_response(index.keys())

        if key is None:
            return json_response(index.keys())

        return json_response(index.get(key, ()))

    def post(self, name, key):
        try:
            obj = json.loads(request.data)
        except ValueError:
            return json_response({
                'error': 'badjson',
                'message': 'The request content could not be interpreted as a JSON object.',
            }, 400)

        index = registry.setdefault(name, dict())
        try:
            registration = index[key]
            return '', 204
        except KeyError:
            registration = index[key] = obj
            url = url_for('registry_api', name=name, key=key)
            return json_response(obj, 201, headers={'Location': url})

    def delete(self, name, key):
        try:
            if key is None:
                del registry[name]
            else:
                del registry[name][key]
        except KeyError as e:
            pass

        return '', 204


registry_view = RegistryAPI.as_view('registry_api')

app.add_url_rule(
    '/registry/', defaults={'name': None, 'key': None}, view_func=registry_view, methods=['GET', 'DELETE'])
app.add_url_rule('/registry/<name>/', defaults={
                 'key': None}, view_func=registry_view, methods=['POST', 'PUT', 'GET', 'DELETE'])
app.add_url_rule('/registry/<name>/<key>', view_func=registry_view,
                 methods=['POST', 'GET', 'PUT', 'DELETE'])


if __name__ == '__main__':
    ddm = DeviceDisplayMatrix()
    ddm.setup_matrix()
    # ddm.restore_app("Buddy List", 1, 1, 2, 1, 1)

    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, host='0.0.0.0', port=5001)
