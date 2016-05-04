
from mongoengine.fields import IntField, StringField, ListField, BooleanField, DictField, EmbeddedDocumentField, FloatField
from mongoengine import DoesNotExist, EmbeddedDocument, Document
from JumpScale import j
from Models import ModelBase

DB = 'jumpscale_cockpitevent'


class Email(ModelBase, Document):
    type = StringField(default='email', choices=('email'), required=True)
    body = StringField(required=True)
    body_type = StringField(choices=('md', 'html', 'text'))
    attachments = DictField()
    cc = ListField(StringField())
    sender = StringField(required=True)
    recipient = StringField(required=True)
    subject = StringField(required=True)
    epoch = IntField(default=j.data.time.getTimeEpoch(), required=True)


class Telegram(ModelBase, Document):
    type = StringField(default='telegram', choices=('telegram'), required=True)
    io = StringField(choices=('input', 'output'), required=True)
    action = StringField(required=True)
    args = DictField()
    epoch = IntField(default=j.data.time.getTimeEpoch(), required=True)


class Alarm(ModelBase, Document):
    type = StringField(default='alarm', choices=('alarm'), required=True)
    service = StringField(required=True)
    method = StringField(required=True)
    msg = StringField(required=True)
    epoch = IntField(default=j.data.time.getTimeEpoch(), required=True)
