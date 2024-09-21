from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+mysqlconnector://uhqp1kcpzvbjn0ja:XolvcP5iWxynYQ5Jcauy@bmrl2p3a5ocsn27lo153-mysql.services.clever-cloud.com:3306/bmrl2p3a5ocsn27lo153"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
