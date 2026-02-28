from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from typing import Literal

app = FastAPI(title="API Biblioteca Digital", version="1.0")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Convierte errores de validación Pydantic en 400 Bad Request."""
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


# Estado del libro según requisitos
ESTADO_LIBRO = Literal["disponible", "prestado"]

libros = [
    {"id": 1, "titulo": "El principito", "autor": "Antoine de Saint-Exupéry", "año": 1943, "paginas": 96, "estado": "disponible"},
    {"id": 2, "titulo": "1984", "autor": "George Orwell", "año": 1949, "paginas": 328, "estado": "disponible"},
    {"id": 3, "titulo": "El alquimista", "autor": "Paulo Coelho", "año": 1988, "paginas": 208, "estado": "disponible"},
]

usuarios = [
    {"id": 1, "nombre": "Juan", "email": "juan@gmail.com"},
    {"id": 2, "nombre": "Maria", "email": "maria@gmail.com"},
    {"id": 3, "nombre": "Pedro", "email": "pedro@gmail.com"},
]

prestamos = [
    {"id": 1, "libro_id": 1, "usuario_id": 1, "fecha_prestamo": "2026-01-01", "fecha_devolucion": "2026-01-05", "activo": True},
    {"id": 2, "libro_id": 2, "usuario_id": 2, "fecha_prestamo": "2026-01-02", "fecha_devolucion": "2026-01-06", "activo": False},
    {"id": 3, "libro_id": 3, "usuario_id": 3, "fecha_prestamo": "2026-01-03", "fecha_devolucion": "2026-01-07", "activo": True},
]

AÑO_ACTUAL = date.today().year




class CrearLibro(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de libro")
    titulo: str = Field(..., min_length=2, max_length=100, description="Título del libro")
    autor: str = Field(..., min_length=2, max_length=100, description="Autor del libro")
    año: int = Field(..., gt=1450, le=AÑO_ACTUAL, description="Año de publicación")
    paginas: int = Field(..., gt=1, description="Número de páginas")
    estado: ESTADO_LIBRO = Field(default="disponible", description="Estado: disponible o prestado")

    @field_validator("estado", mode="before")
    @classmethod
    def estado_permitido(cls, v):
        if v not in ("disponible", "prestado"):
            raise ValueError('Estado debe ser "disponible" o "prestado"')
        return v


class CrearUsuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del usuario")
    email: str = Field(..., min_length=5, max_length=100, description="Email válido")

    @field_validator("email")
    @classmethod
    def email_valido(cls, v: str):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Correo electrónico no válido")
        return v


class CrearPrestamo(BaseModel):
    id: int = Field(..., gt=0, description="Identificador del préstamo")
    libro_id: int = Field(..., gt=0, description="ID del libro")
    usuario_id: int = Field(..., gt=0, description="ID del usuario")
    fecha_prestamo: str = Field(..., description="Fecha de préstamo YYYY-MM-DD")
    fecha_devolucion: str = Field(..., description="Fecha de devolución YYYY-MM-DD")



@app.post("/v1/libros/", tags=["Libros"], status_code=201)
async def registrar_libro(libro: CrearLibro):
    """Registra un nuevo libro. 201 Created. 400 si faltan datos o nombre no válido."""
    if any(lb["id"] == libro.id for lb in libros):
        raise HTTPException(status_code=400, detail="El id de libro ya existe")
    nuevo = libro.model_dump()
    libros.append(nuevo)
    return {"mensaje": "Libro creado", "datos": nuevo}


@app.get("/v1/libros/", tags=["Libros"])
async def listar_libros(disponibles_only: bool = Query(False, description="Solo libros disponibles")):
    """Lista todos los libros. Opción ?disponibles_only=true para solo disponibles."""
    lista = libros
    if disponibles_only:
        lista = [lb for lb in libros if lb.get("estado") == "disponible"]
    return {"total": len(lista), "libros": lista}


@app.get("/v1/libros/buscar", tags=["Libros"])
async def buscar_libro_por_nombre(nombre: str = Query(..., min_length=1)):
    """Busca libros por nombre (coincidencia parcial)."""
    nombre_lower = nombre.lower().strip()
    encontrados = [lb for lb in libros if nombre_lower in lb["titulo"].lower()]
    return {"total": len(encontrados), "libros": encontrados}



def _libro_por_id(libro_id: int):
    for lb in libros:
        if lb["id"] == libro_id:
            return lb
    return None


def _prestamo_por_id(prestamo_id: int):
    for i, p in enumerate(prestamos):
        if p["id"] == prestamo_id:
            return i, p
    return None, None


@app.post("/v1/prestamos/", tags=["Préstamos"], status_code=201)
async def registrar_prestamo(prestamo: CrearPrestamo):
    """Registra el préstamo de un libro a un usuario. 201 Created. 409 si el libro ya está prestado."""
    libro = _libro_por_id(prestamo.libro_id)
    if not libro:
        raise HTTPException(status_code=400, detail="Libro no encontrado")
    if libro.get("estado") == "prestado":
        raise HTTPException(status_code=409, detail="El libro ya está prestado")
    if any(p["id"] == prestamo.id for p in prestamos):
        raise HTTPException(status_code=400, detail="El id de préstamo ya existe")
    if not any(u["id"] == prestamo.usuario_id for u in usuarios):
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    nuevo = prestamo.model_dump()
    nuevo["activo"] = True
    prestamos.append(nuevo)
    for lb in libros:
        if lb["id"] == prestamo.libro_id:
            lb["estado"] = "prestado"
            break
    return {"mensaje": "Préstamo registrado", "datos": nuevo}


@app.put("/v1/prestamos/{prestamo_id}/devolver", tags=["Préstamos"])
async def marcar_libro_devuelto(prestamo_id: int):
    """Marca un libro como devuelto. 200 OK. 409 si el registro de préstamo ya no existe."""
    idx, prestamo = _prestamo_por_id(prestamo_id)
    if prestamo is None:
        raise HTTPException(status_code=409, detail="El registro de préstamo no existe")
    if not prestamo.get("activo", True):
        raise HTTPException(status_code=409, detail="El préstamo ya fue devuelto")

    prestamo["activo"] = False
    prestamos[idx] = prestamo
    for lb in libros:
        if lb["id"] == prestamo["libro_id"]:
            lb["estado"] = "disponible"
            break
    return {"mensaje": "Libro devuelto correctamente", "prestamo_id": prestamo_id}


@app.delete("/v1/prestamos/{prestamo_id}", tags=["Préstamos"])
async def eliminar_prestamo(prestamo_id: int):
    """Elimina el registro de un préstamo. 200 OK. 409 si el registro ya no existe."""
    idx, prestamo = _prestamo_por_id(prestamo_id)
    if prestamo is None:
        raise HTTPException(status_code=409, detail="El registro de préstamo no existe")

    libro_id = prestamo["libro_id"]
    prestamos.pop(idx)
    if prestamo.get("activo", True):
        for lb in libros:
            if lb["id"] == libro_id:
                lb["estado"] = "disponible"
                break
    return {"mensaje": "Préstamo eliminado", "prestamo_id": prestamo_id}



@app.get("/v1/usuarios/", tags=["Usuarios"])
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}


@app.post("/v1/usuarios/", tags=["Usuarios"], status_code=201)
async def registrar_usuario(usuario: CrearUsuario):
    if any(u["id"] == usuario.id for u in usuarios):
        raise HTTPException(status_code=400, detail="El id de usuario ya existe")
    nuevo = usuario.model_dump()
    usuarios.append(nuevo)
    return {"mensaje": "Usuario creado", "datos": nuevo}


@app.get("/v1/prestamos/", tags=["Préstamos"])
async def leer_prestamos():
    return {"total": len(prestamos), "prestamos": prestamos}
