from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "postgresql://dtc_clean:12345pass@localhost:5432/dtc_clean_db"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
