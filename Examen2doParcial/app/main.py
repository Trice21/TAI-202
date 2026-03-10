from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel, Field
import asyncio
from typing import Literal
from typing import Optional
from pydantic import field_validator
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from datetime import date
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date, time
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
    {"id": 1, "fecha": "03-02-2026", "a_nombre_de": "Joshua", "hora": "12:00","estado": "Cancelada", "no_personas": 1}
]



class CrearReservacion(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    a_nombre_de: str = Field(..., min_length=6, description="Nombre usuario")
    no_personas: int = Field(..., gt=0, ge=0, le=10,description="Numero de personas que reservan")
    fecha: date
    hora: str

    @field_validator("hora")
    @classmethod
    def validar_hora(cls, v):
        hora = datetime.strptime(v, "%H:%M").time()
        inicio = time(8, 0)
        fin = time(22, 0)

        if hora < inicio or hora > fin:
            raise ValueError("La hora debe estar entre 08:00 y 22:00")
        return v 
 
            
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

@app.put("/v1/reservaciones/{reservacion_id}/confirmar", tags=["Reservaciones"])
async def confirmar_reservacion(reservacion_id: int):
    """Marca una reservacion como confirmada. 200 OK. 409 si el registro de Reservacion ya no existe."""
    reservacion = reserva_por_id(reservacion_id)
    if reservacion is None:
        raise HTTPException(status_code=409, detail="El registro de préstamo no existe")
    for rv in reservaciones:
       if rv["id"] == reservacion_id:
            rv["estado"] = "Confirmada"
            break
    return {"mensaje": "Reservacion confirmada correctamente", "Reservacion_id": reservacion_id}

@app.put("/v1/reservaciones/{reservacion_id}/cancelar", tags=["Reservaciones"])
async def cancelar_reservacion(reservacion_id: int, str = Depends(verificar_peticion)):
    """Marca una reservacion como confirmada. 200 OK. 409 si el registro de Reservacion ya no existe."""
    reservacion = reserva_por_id(reservacion_id)
    if reservacion is None:
        raise HTTPException(status_code=409, detail="El registro de préstamo no existe")
    for rv in reservaciones:
       if rv["id"] == reservacion_id:
            rv["estado"] = "Cancelada"
            break
    return {"mensaje": "Reservacion cancelada correctamente", "Reservacion_id": reservacion_id}
@app.post("/v1/reservaciones/", tags=["HTTP CRUD"], status_code=status.HTTP_201_CREATED)
async def agregar_usuarios(reservacion: CrearReservacion, str = Depends(verificar_peticion)):
    if any(rv["id"] == reservacion.id for rv in reservaciones):
        raise HTTPException(status_code=400, detail="El id ya existe")

    nuevo = reservaciones.model_dump()
    reservaciones.append(nuevo)
    return {"mensaje": "Reservacion creada", "datos": nuevo}