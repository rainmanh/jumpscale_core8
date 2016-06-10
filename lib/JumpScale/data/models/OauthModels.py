from mongoengine.fields import IntField, StringField, ListField, DictField, DateTimeField
from mongoengine import Document
from JumpScale import j
from Models import ModelBase, extend
from datetime import datetime

DB = 'jumpscale_oauth'

default_meta = {'allow_inheritance': True, "db_alias": DB}

class AccessToken(ModelBase, Document):
    access_token = StringField(required=True)
    scope = StringField(required=True)
    info = DictField()
    token_type = StringField(required=True)
    expire = IntField(default=j.data.time.getEpochFuture('1d'))
    # TODO, expireAfterSeconds doesn't work
    meta = extend(default_meta, {
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 3600 * 24}
        ]
    })
    created = DateTimeField(default=datetime.now)


class JWTToken(ModelBase, Document):
    jwt_token = StringField(required=True)
    expire = IntField(default=j.data.time.getEpochFuture('1d'))
    created = DateTimeField(default=datetime.now)
    username = StringField(required=False)
    # TODO, expireAfterSeconds doesn't work
    meta = extend(default_meta, {
        'indexes': [
            'username',
            {'fields': ['created'], 'expireAfterSeconds': 3600 * 24}
        ]
    })
