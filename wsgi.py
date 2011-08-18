#!/usr/bin/env python
# coding: utf-8
from flask import Flask, redirect, url_for, request, session
from lxml.builder import E
from lxml.cssselect import CSSSelector
from lxml.html import fragments_fromstring
from lxml.html.clean import Cleaner
from template import POST, SPACER, POST_FORM, embed_nodes
from blog import Post
from copy import copy
from elixir import setup_all, create_all, metadata, session as db_session
from sqlalchemy import desc
from hashlib import sha1
from flaskutil import restfuljson

app = Flask(__name__)
app.debug = True
app.secret_key = '\x151\xdcT\xc4\x91\xf50\xcbG8\xa9o\xb3\x90\x8b\x8c\xd8B\x95\xed\xf4\x8cq'

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
    CSSSelector('.datetime')(post)[0].text = datetime.strftime("%I:%M on %A the %%s of %B, %Y") % niceday(datetime)
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

@app.route('/add', methods=['GET'])
#@embed_nodes("Add/Edit")
def add_edit():
    fs = FieldSet(Post)

    fs.configure(options=[fs.datetime.hidden(),
                          fs.content.textarea()])

    #for fragment in fragments_fromstring(fs.render()):
    #    yield fragment
    return fs.render()

@app.route('/login', methods=['GET', 'POST'])
@embed_nodes()
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
