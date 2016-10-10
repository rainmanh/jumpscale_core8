# Cookbook SQL Alchemy

## init

- create a dir in which all following files will be stored

## Model.py

this is the file which will build your database model

```
from JumpScale import j
from sqlalchemy.orm import relationship, backref, sessionmaker,class_mapper
from sqlalchemy import *
from sqlalchemy.event import listen

db=j.db.sqlalchemy
Base=db.getBaseClass()

class Email(Base):
    __tablename__ = 'email'
    email= Column(String, primary_key=True, nullable=False)
    user_id=Column(String, ForeignKey('user.id'))

    def __repr__(self):
        return "email: %s" % (self.email)

listen(Email.email, 'set', db.validate_email, retval=True)

class Mobile(Base):
    __tablename__ = 'mobile'
    mobile= Column(String, primary_key=True, nullable=False)
    user_id=Column(String, ForeignKey('user.id'))

    def __repr__(self):
        return "mobile: %s" % (self.mobile)

    #with this you can implement == feature on object, is good trick to have easier comparisons in e.g. lists
    def __eq__(self,other):
        return self.mobile==other.lower()

    def __ne__(self,other):
        return not self.__ne__(other)

listen(Mobile.mobile, 'set', db.validate_tel, retval=True)

class Sync(Base):
    __tablename__ = 'sync'
    id=Column(Integer, primary_key=True)
    category= Column(String, nullable=False)
    user_id=Column(String, ForeignKey('user.id'))
    lastdate= Column(Integer,default=j.data.time.getTimeEpoch())
    state=Column(String,default="?")
    sqlite_autoincrement=True

    def __repr__(self):
        return "sync: %s:%s" % (self.category, self.state)

    def __eq__(self,other):
        return self.category.lower()==other.lower()

    def __ne__(self,other):
        return not self.__ne__(other)

listen(Sync.state, 'set', db.validate_lower_strip, retval=True)

user2group = Table('user2group', Base.metadata,
    Column('user', Integer, ForeignKey('user.id')),
    Column('group', Integer, ForeignKey('group.id'))
)

class Group(Base):
    __tablename__ = 'group'
    _totoml=True    
    id= Column(String, primary_key=True, nullable=False)
    users = relationship("User",secondary=user2group,backref="groups")
    description = Column(String,default="")

    def __repr__(self):
        return "group: %s" % (self.id)

class User(Base):
    __tablename__ = 'user'
    _totoml=True
    id = Column(String, primary_key=True, nullable=False)
    firstname = Column(String,index=True,default="")
    lastname = Column(String,index=True,default="")
    mobiles = relationship("Mobile", backref=backref('user'))
    skype = Column(String,default="",index=True)
    description = Column(String,default="")
    git_aydo = Column(String,default="")
    git_github = Column(String,default="")
    telegram = Column(String,default="",index=True)
    emails = relationship("Email", backref=backref('user'))
    sync = relationship("Sync", backref=backref('user'))
    function = Column(String,default="")
    reportsTo = Column(String,default="")
    org = "gig"

    def _tomlpath(self,sqlalchemy):
        path="%s/%s/%s/%s.toml"%(sqlalchemy.tomlpath,self.__tablename__,self.org,self.id.lower())
        return path

    def __repr__(self):
        return "name='%s', fullname='%s'" % (self.firstname, self.lastname)

listen(User.telegram, 'set', db.validate_tel, retval=True)
listen(User.skype, 'set', db.validate_lower_strip, retval=True)
listen(User.firstname, 'set', db.validate_lower_strip, retval=True)
listen(User.lastname, 'set', db.validate_lower_strip, retval=True)
listen(User.git_aydo, 'set', db.validate_lower_strip, retval=True)
listen(User.git_github, 'set', db.validate_lower_strip, retval=True)
```

## Example.py

example to use your model

```
from JumpScale import j
from Model import *

db=j.db.sqlalchemy

sql=db.get(sqlitepath=j.dirs.varDir+"/toml.db",tomlpath='/tmp/data',connectionstring='')

u=User(id="kds")
sql.session.add(u)
sql.session.commit()
```

## Fine example

### TODO:
