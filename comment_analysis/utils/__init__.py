from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

engine = create_engine('mysql+pymysql://root:{0}@localhost:3306/jd?charset=utf8mb4'.format('123456'))
# engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)
SessionCls = sessionmaker(bind=engine)
sql_session = SessionCls()