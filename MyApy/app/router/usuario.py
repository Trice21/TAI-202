from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
import asyncio
from typing import Optional
from app.models.usuario import CrearUsuario
from app.models.usuario import PatchUsuario
from app.data.database import usuarios
from app.security.auth import verificar_peticion

router = APIRouter(
    prefix= "/v1/usuarios",
    tags = ["HTTP CRUD"]
)
@router.get("/")
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}

@router.post("/", status_code=status.HTTP_201_CREATED)
async def agregar_usuarios(usuario: CrearUsuario):
    if any(usr["id"] == usuario.id for usr in usuarios):
        raise HTTPException(status_code=400, detail="El id ya existe")

    nuevo = usuario.model_dump()
    usuarios.append(nuevo)
    return {"mensaje": "Usuario Creado", "datos": nuevo}

@router.put("/{usuario_id}")
async def actualizar_usuario_completo(usuario_id: int, usuario_actualizado: CrearUsuario):
    for indice, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            data = usuario_actualizado.model_dump()
            data["id"] = usuario_id
            usuarios[indice] = data
            return {"mensaje": "Usuario actualizado", "datos": usuarios[indice]}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.patch("/")
async def actualizar_usuario_parcial(usuario_id: int, datos_parciales: PatchUsuario):
    for usr in usuarios:
        if usr["id"] == usuario_id:
            cambios = datos_parciales.model_dump(exclude_unset=True)
            usr.update(cambios)
            return {"mensaje": "Usuario actualizado parcialmente", "usuario": usr}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.delete("/{usuario_id}")
async def eliminar_usuario(usuario_id: int, usuario_Auth: str = Depends(verificar_peticion)):
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuario_eliminado = usuarios.pop(i)
            return {"mensaje": "Usuario eliminado",
                     "usuario": usuario_eliminado,
                     "eliminado_por": f"{usuario_Auth}"}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")