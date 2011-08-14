# coding: UTF-8
from elixir import Entity, Field, DateTime, Unicode, UnicodeText, ManyToMany, Boolean
import datetime

class Post(Entity):

    """
    Blog post class
    """

    title = Field(Unicode(30), unique=True)
    datetime = Field(DateTime, default=datetime.datetime.utcnow(), required=True)
    content = Field(UnicodeText, required=True)
    published = Field(Boolean, default=False, required=True)

    # relationships
    tags = ManyToMany('Tag')

    def __repr__(self):
        return '<%(cls)s %(datetime)s "%(title)s">' % dict(cls=self.__class__.__name__,
                                                           datetime=self.datetime,
                                                           title=self.title)

class Tag(Entity):

    """
    Simple tag to be applied to blog posts
    """

    name = Field(Unicode(10), primary_key=True)

    # relationships
    posts = ManyToMany('Post')

    def __repr__(self):
        return '<%(cls)s %(name)s>' % dict(cls=self.__class__.__name__,
                                           name=self.name)
