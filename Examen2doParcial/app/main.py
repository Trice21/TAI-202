from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel, Field
import asyncio
from typing import Literal
from typing import Optional
from pydantic import field_validator
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from datetime import date

app = FastAPI()

seguridad = HTTPBasic()
ESTADO_RESERVA= Literal["Confirmada", "Cancelada"]

def verificar_peticion(credenciales: HTTPBasicCredentials = Depends(seguridad)):
    usuario_correcto = secrets.compare_digest(credenciales.username, "admin")
    contrasena_correcta = secrets.compare_digest(credenciales.password, "rest123")
    if not (usuario_correcto and contrasena_correcta):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Credenciales inválidas"
        )
    return credenciales.username


reservaciones= [
    {"id": 1, "fecha": "03-02-2026", "a_nombre_de": "Joshua", "hora": "12:00","estado": "Confirmada"}
]


        
@app.get("/v/reservaciones/", tags=["HTTP CRUD"])
async def listar_reservaciones(str = Depends(verificar_peticion)):
    return {"total": len(reservaciones), "reservaciones": reservaciones}


def reserva_por_id(reservacion_id: int):
    for rv in reservaciones:
        if rv["id"] == reservacion_id:
            return rv
    return None

@app.get("/v1/reservaciones/{reservacion_id}", tags=["HTTP CRUD"])
async def dispositivo_por_id(reservacion_id: int):
    for rv in reservaciones:
        if rv["id"] == reservacion_id:
            return rv
    raise HTTPException(status_code=404, detail="Reservacion no encontrada")