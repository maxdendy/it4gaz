from src.config import PGSQL_PASSWORD, PGSQL_USERNAME, PGSQL_HOST

from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, Float, Sequence, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

database_URL = f'postgresql://{PGSQL_USERNAME}:{PGSQL_PASSWORD}@{PGSQL_HOST}/it4gaz'
engine = create_engine(database_URL)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class Data(Base):
    __tablename__ = 'data'

    id = Column(Integer, Sequence('data_id_seq'), primary_key=True)
    Time = Column(DateTime)
    T_K_1 = Column(Float)
    T_K_2 = Column(Float)
    T_K_3 = Column(Float)
    T_L_1 = Column(Float)
    T_L_2 = Column(Float)
    T_L_3 = Column(Float)
    T_Up_1 = Column(Float)
    T_Up_2 = Column(Float)
    T_Up_3 = Column(Float)
    T_1 = Column(Float)


Base.metadata.create_all(engine)


def readFromCSV(path):
    with open(path, 'r') as f:
        strin = f.read().strip().split('\n')
        for i in range(1, len(strin)):
            j = strin[i].split(';')
            j = [j[0]] + [float(o.replace(',', '.')) for o in j[1:]]
            data = Data(Time=datetime.strptime(j[0], '%Y-%m-%dT%H:%M:%S,%f'), T_K_1=j[1], T_K_2=j[2], T_K_3=j[3],
                        T_L_1=j[4], T_L_2=j[5], T_L_3=j[6], T_Up_1=j[7], T_Up_2=j[8], T_Up_3=j[9], T_1=j[10])
            Session.add(data)
        Session.commit()
