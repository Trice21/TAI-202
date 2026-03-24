from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from app.models.usuario import CrearUsuario, PatchUsuario
from app.security.auth import verificar_peticion
from app.data.db import get_db
from app.data.usuario import usuario as dbUsuario

router = APIRouter(
    prefix="/v1/usuarios",
    tags=["HTTP CRUD"]
)

@router.get("/")
async def leer_usuarios(db: Session = Depends(get_db)):
    query_usuarios = db.query(dbUsuario).all()

    usuarios_json = [
        {
            "id": usr.id,
            "nombre": usr.nombre,
            "edad": usr.edad
        }
        for usr in query_usuarios
    ]

    return {
        "status": 200,
        "total": len(usuarios_json),
        "usuarios": usuarios_json
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def agregar_usuarios(usuarioP: CrearUsuario, db: Session = Depends(get_db)):
    nuevo_usuario = dbUsuario(
        nombre=usuarioP.nombre,
        edad=usuarioP.edad
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario creado",
        "datos": {
            "id": nuevo_usuario.id,
            "nombre": nuevo_usuario.nombre,
            "edad": nuevo_usuario.edad
        }
    }

@router.put("/{usuario_id}")
async def actualizar_usuario_completo(
    usuario_id: int,
    usuario_actualizado: CrearUsuario,
    db: Session = Depends(get_db)
):
    usuario_db = db.query(dbUsuario).filter(dbUsuario.id == usuario_id).first()

    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario_db.nombre = usuario_actualizado.nombre
    usuario_db.edad = usuario_actualizado.edad

    db.commit()
    db.refresh(usuario_db)

    return {
        "mensaje": "Usuario actualizado",
        "datos": {
            "id": usuario_db.id,
            "nombre": usuario_db.nombre,
            "edad": usuario_db.edad
        }
    }

@router.patch("/{usuario_id}")
async def actualizar_usuario_parcial(
    usuario_id: int,
    datos_parciales: PatchUsuario,
    db: Session = Depends(get_db)
):
    usuario_db = db.query(dbUsuario).filter(dbUsuario.id == usuario_id).first()

    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cambios = datos_parciales.model_dump(exclude_unset=True)

    for campo, valor in cambios.items():
        setattr(usuario_db, campo, valor)

    db.commit()
    db.refresh(usuario_db)

    return {
        "mensaje": "Usuario actualizado parcialmente",
        "usuario": {
            "id": usuario_db.id,
            "nombre": usuario_db.nombre,
            "edad": usuario_db.edad
        }
    }

@router.delete("/{usuario_id}")
async def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_Auth: str = Depends(verificar_peticion)
):
    usuario_db = db.query(dbUsuario).filter(dbUsuario.id == usuario_id).first()

    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    datos_eliminados = {
        "id": usuario_db.id,
        "nombre": usuario_db.nombre,
        "edad": usuario_db.edad
    }

    db.delete(usuario_db)
    db.commit()

    return {
        "mensaje": "Usuario eliminado",
        "usuario": datos_eliminados,
        "eliminado_por": usuario_Auth
    }