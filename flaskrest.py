# coding: utf-8
from flask import make_response
from functools import wraps
import json

def restfuljson(flask_app, route, cls=None):
    """
    A _class_ decorator to make restful interfaces easier
    """
    def add_json_routes(c):
        for fun in 'get', 'head', 'post', 'put', 'delete':
            f = getattr(c, 'rest_' + fun)
            @flask_app.route(route, methods=[fun.upper()])
            @wraps(f)
            def wrflask_apper(_f=f, *args, **kwargs):
                response = make_response(json.dumps(_f(*args, **kwargs)))
                response.headers['Content-Type'] = 'text/json'
                return response

        return c

    if cls is None:
        # called as decorator
        return add_json_routes

    add_json_routes(cls)
