#!/usr/bin/env python
# coding: utf-8

from nodeblogapp import app as application

if __name__ == "__main__":
    application.debug = True
    application.run(host='0.0.0.0', port=8000)
