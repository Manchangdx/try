from sqlalchemy import create_engine, Column, String, Integer, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql://root@localhost/shiyanlou?charset=utf8')
Base = declarative_base(engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True)
    is_vip = Column(Boolean, default=0)
    status = Column(String(64))
    school_job = Column(String(64))
    level = Column(Integer)
    join_date = Column(Date)
    learn_courses_num = Column(Integer)

if __name__ == '__main__':
    Base.metadata.create_all()
