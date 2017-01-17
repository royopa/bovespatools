import sqlalchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Date, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

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
    bdi = Column(SmallInteger, primary_key = True)
    # Asset symbols may transition from one company to another
    company_id = Column(Integer, ForeignKey('company.id'), primary_key = True)
    company = relationship(Company)
    pass

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
    volume = Column(Integer)
    asset = relationship(Asset)
    # Due to grouping and splitting, assets can have their prices artificially changed
    price_factor_quotient = Column(Integer)
    price_factor_dividend = Column(Integer)
    pass

engine = create_engine('sqlite:///'+database_file)
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

