from sqlalchemy import column, Integer, String
from app.data.db import Base

class usuario(Base):
    _tablename_ = "usuarios"
    id = column(Integer, primary_key=True, index=True)
    nombre = column(String)
    edad = column(Integer)