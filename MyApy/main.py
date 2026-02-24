from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

usuarios = [
    {"id": 1, "nombre": "Fany", "edad": 21},
    {"id": 2, "nombre": "Ali", "edad": 21},
    {"id": 3, "nombre": "Dulce", "edad": 21},
]

class CrearUsuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=3, max_length=50, example="Juanita")
    edad: int = Field(..., ge=1, le=123, description="Edad valida entre 1 y 123")

class PatchUsuario(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=50, example="Juanita")
    edad: Optional[int] = Field(None, ge=1, le=123, description="Edad valida entre 1 y 123")

@app.get("/v1/usuarios/", tags=["HTTP CRUD"])
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}

@app.post("/v1/usuarios/", tags=["HTTP CRUD"], status_code=status.HTTP_201_CREATED)
async def agregar_usuarios(usuario: CrearUsuario):
    if any(usr["id"] == usuario.id for usr in usuarios):
        raise HTTPException(status_code=400, detail="El id ya existe")

    nuevo = usuario.model_dump()
    usuarios.append(nuevo)
    return {"mensaje": "Usuario Creado", "datos": nuevo}

@app.put("/v1/usuarios/{usuario_id}", tags=["HTTP CRUD"])
async def actualizar_usuario_completo(usuario_id: int, usuario_actualizado: CrearUsuario):
    for indice, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            data = usuario_actualizado.model_dump()
            data["id"] = usuario_id
            usuarios[indice] = data
            return {"mensaje": "Usuario actualizado", "datos": usuarios[indice]}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.patch("/v1/usuarios/{usuario_id}", tags=["HTTP CRUD"])
async def actualizar_usuario_parcial(usuario_id: int, datos_parciales: PatchUsuario):
    for usr in usuarios:
        if usr["id"] == usuario_id:
            cambios = datos_parciales.model_dump(exclude_unset=True)
            usr.update(cambios)
            return {"mensaje": "Usuario actualizado parcialmente", "usuario": usr}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.delete("/v1/usuarios/{usuario_id}", tags=["HTTP CRUD"])
async def eliminar_usuario(usuario_id: int):
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuario_eliminado = usuarios.pop(i)
            return {"mensaje": "Usuario eliminado", "usuario": usuario_eliminado}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")