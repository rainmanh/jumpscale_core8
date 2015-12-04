from JumpScale import j

def sQLAlchemy():
    from .SQLAlchemy import SQLAlchemyFactory
    return SQLAlchemyFactory()


j.clients._register('sqlalchemy', sQLAlchemy)
