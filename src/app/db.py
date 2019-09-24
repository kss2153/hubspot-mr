import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_host = os.environ.get('CLOUD_SQL_HOST')

engine_url = 'mysql+pymysql://{}:{}@{}/{}'.format(db_user, db_password, db_host, db_name)
engine = create_engine(engine_url, pool_size=3)

SqlSession = sessionmaker(bind=engine)
