from sqlalchemy import create_engine, Column, String, Integer, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql://root@localhost/shiyanlou?charset=utf8')
Base = declarative_base(engine)
session = sessionmaker(engine)()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True)
    is_vip = Column(Boolean, default=False)
    status = Column(String(64))
    school_job = Column(String(64))
    level = Column(Integer)
    join_date = Column(Date)
    learn_courses_num = Column(Integer)


class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    image = Column(String(128))
    author = Column(String(32))

if __name__ == '__main__':
    Base.metadata.create_all()
