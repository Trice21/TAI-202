from fastapi import FastAPI, status, HTTPException, Depends
import asyncio
from typing import Optional
from app.models.usuario import CrearUsuario
from app.models.usuario import PatchUsuario
from app.data.database import usuarios
from app.security import verificar_peticion

router = APIRouter(
    prefix= "/v1/misc",
    tags = ["MISC HTTP"]
)