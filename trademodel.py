import sqlalchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Float, String, Date, BigInteger, SmallInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


"""
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

logging.basicConfig()
logger = logging.getLogger("myapp.sqltime")
logger.setLevel(logging.DEBUG)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug("Start Query: %s", statement)

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    logger.debug("Query Complete!")
    logger.debug("Total Time: %f", total)
"""


Base = declarative_base()
database_file = './bovespa.db'

class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key = True, autoincrement = True)
    short_name = Column(String(12), unique = True)
    pass

class Asset(Base):
    __tablename__ = 'asset'
    code = Column(String(12), primary_key = True)
    bdi = Column(SmallInteger, primary_key = True, autoincrement = False)
    # Asset symbols may transition from one company to another
    company_id = Column(Integer, ForeignKey('company.id'), primary_key = True)
    isin = Column(String(12))
    company = relationship(Company)
    pass

class AssetActions(Base):
    __tablename__ = 'asset_actions'
    asset_code = Column(String(12), ForeignKey('asset.code'), primary_key = True)
    action_type = Column(String(13), primary_key = True)
    ex_date = Column(Date, primary_key = True)
    approval_date = Column(Date)
    factor = Column(Float)
    issued_asset = Column(String(12))
    remarks = Column(Text)
    asset = relationship(Asset)

class SpotMarket(Base):
    __tablename__ = 'spot_market'
    date = Column(Date, primary_key = True)
    asset_code = Column(String(12), ForeignKey('asset.code'), primary_key = True)
    opening_price = Column(Integer)
    max_price = Column(Integer)
    min_price = Column(Integer)
    avg_price = Column(Integer)
    last_price = Column(Integer)
    best_buy_offer_price = Column(Integer)
    best_sell_offer_price = Column(Integer)
    volume = Column(BigInteger)
    asset = relationship(Asset)
    price_factor = Column(Integer)
    pass

engine = create_engine('sqlite:///'+database_file)
#engine = create_engine('mysql://root:root@localhost/')
#engine.execute("USE trade")

Base.metadata.create_all(engine)

def get_session():
    DBSession = sessionmaker(bind = engine)
    return DBSession()

def stringify_query(query, kwargs):
    """
    Sample usage:
    print stringify_query(session.query(model).filter_by(**kwargs), kwargs)
    """
    from sqlalchemy.dialects import sqlite
    s = str(query.statement.compile(dialect=sqlite.dialect()))
    for key in kwargs:
        s = s.replace('?', '\''+str(kwargs[key])+'\'', 1)
        pass
    return s

def get_or_create(session, model, kwargs):
    instance = session.query(model).filter_by(**kwargs['primary_keys']).first()
    if instance:
        return instance
    else:
        model_data = kwargs['primary_keys'].copy()
        if 'regular_keys' in kwargs:
            model_data.update(kwargs['regular_keys'])

        instance = model(**model_data)
        session.add(instance)
        return instance
    pass

