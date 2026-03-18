from fastapi import FastAPI, APIRouter
from app.router import usuario
#Instancia del servidor
app = FastAPI(
    title = "Mi Primer API"
)

app.include_router(usuario.router)



