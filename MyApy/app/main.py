from fastapi import FastAPI
from app.router import usuario
from app.data.db import Base, engine
from app.data.usuario import usuario as usuarioDB

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mi Primer API",
    description="Jesús Eloy Vargas Rea",
    version="1.0"
)

app.include_router(usuario.router)