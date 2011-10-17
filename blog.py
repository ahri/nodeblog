#!/usr/bin/env python
# coding: utf-8
from flask import Flask, redirect, url_for, request, session
from lxml.builder import E
from lxml.cssselect import CSSSelector
from lxml.html import fragments_fromstring
from lxml.html.clean import Cleaner
from template import POST, SPACER, POST_FORM, embed_nodes
from html import Post
from copy import copy
from elixir import setup_all, create_all, metadata, session as db_session
from sqlalchemy import desc
from hashlib import sha1
from flaskutil import restfuljson
from uuid import uuid4

app = Flask(__name__)
app.secret_key = uuid4().hex

metadata.bind = 'sqlite:///foo.db'
metadata.bind.echo = True

PASSWORD_SALT = 'nodeblog'
PASSWORD_HASH = 'cba8c7803bed2d4a7106b3a31876081e18d188ad'

cleaner_trusted = Cleaner(page_structure=False)
cleaner_untrusted = Cleaner(page_structure=False)

setup_all()
create_all()

@restfuljson(app, '/rest/moo')
class Moo:
    @classmethod
    def get_caller(cls):
        import inspect
        return inspect.stack()[1][3]

    @classmethod
    def rest_get(cls):
        return cls.get_caller()

    @classmethod
    def rest_head(cls):
        return cls.get_caller()

    @classmethod
    def rest_post(cls):
        return cls.get_caller()

    @classmethod
    def rest_put(cls):
        return cls.get_caller()

    @classmethod
    def rest_delete(cls):
        return cls.get_caller()

@app.teardown_request
def teardown_request(exception):
    db_session.flush()

def niceday(dt):
    day = int(dt.strftime('%d'))
    if 4 <= day <= 20 or 24 <= day <= 30:
        return str(day) + "th"
    else:
        return str(day) + ["st", "nd", "rd"][day % 10 - 1]

def post_node(title, datetime, content):
    post = copy(POST)
    CSSSelector('.title .text')(post)[0].text = title
    CSSSelector('.datetime')(post)[0].text = datetime.strftime("%H:%M on %A the %%s of %B, %Y") % niceday(datetime)
    content_css = CSSSelector('.content')(post)[0]
    for fragment in fragments_fromstring(cleaner_trusted.clean_html(content)):
        content_css.append(fragment)

    return post

@embed_nodes(app,
             "Everything looks perfect from far away",
             '/',
             css=['http://static.ahri.net/css/blog.css'],
             js=['http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js',
                 'http://static.ahri.net/js/blog.js',
                ],
             removals=["//*[@class='spacer'][last()]"])
def blog():
    for post in Post.query.filter(Post.published==True).order_by(desc(Post.datetime)):
        yield post_node(post.title, post.datetime, post.content)
        yield copy(SPACER)

#------------CRUD
@embed_nodes(app, "Add", '/add', methods=['GET'])
def add():
    yield copy(POST_FORM)

@embed_nodes(app, "Add", '/add', methods=['POST'])
def add_handle():
    yield E.p("handle the post")

@embed_nodes(app, "Edit", '/edit/<int:post_id>', methods=['GET'])
def edit(post_id):
    form = copy(POST_FORM)
    yield form

@embed_nodes(app, "Edit", '/edit/<int:post_id>', methods=['POST'])
def edit_handle(post_id):
    yield E.p("handle the post")
#------------CRUD

@embed_nodes(app, "Login", '/login', methods=['GET', 'POST'])
def login():
    try:
        hsh = sha1(request.form.get('password') + PASSWORD_SALT)
        if hsh.hexdigest() == PASSWORD_HASH:
            session['logged_in'] = True
            return redirect(url_for('add'))

    except TypeError:
        pass

    return [E.form(
        E.input(type='password', name='password'),
        E.input(type='submit', value='Login'),
        method='post',
    )]

@embed_nodes(app, "CV", '/cv')
def cv():
    yield E.p("insert CV here")
