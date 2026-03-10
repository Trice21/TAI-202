from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Literal

app = FastAPI()

ESTADO_dispositivo = Literal["disponible", "asignado"]

dispositivos = [
    {"id": 1, "nombre": "Laptop", "marca": "Dell", "modelo": "XPS 13", "anio": 2020, "numero_serie": "12345", "estado": "asignado"},
    {"id": 2, "nombre": "Smartphone", "marca": "Samsung", "modelo": "Galaxy S21", "anio": 2021, "numero_serie": "67890", "estado": "asignado"},
    {"id": 3, "nombre": "Tablet", "marca": "Apple", "modelo": "iPad Air", "anio": 2020, "numero_serie": "54321", "estado": "asignado"},
]

usuarios = [
    {"id": 1, "nombre": "Fany", "departamento": "TI", "correo": "fany@example.com"},
    {"id": 2, "nombre": "Ali", "departamento": "Recursos Humanos", "correo": "ali@example.com"},
    {"id": 3, "nombre": "Dulce", "departamento": "Marketing", "correo": "dulce@example.com"},
]

asignaciones = [
    {"id": 1, "usuario_id": 1, "dispositivo_id": 1, "activo": True},
    {"id": 2, "usuario_id": 2, "dispositivo_id": 2, "activo": True},
    {"id": 3, "usuario_id": 3, "dispositivo_id": 3, "activo": True},
]

def dispositivo_por_id_pres(dispositivo_id: int):
    for dp in dispositivos:
        if dp["id"] == dispositivo_id:
            return dp
    return None

def asignacion_por_id(asignacion_id: int):
    for i, p in enumerate(asignaciones):
        if p["id"] == asignacion_id:
            return i, p
    return None, None

class CrearDispositivo(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de dispositivo")
    nombre: str = Field(..., min_length=3, example="Laptop", description="Nombre")
    marca: str = Field(..., min_length=2, description="Marca")
    modelo: str = Field(..., min_length=1, description="Modelo")
    anio: int = Field(..., gt=2000, description="Año del dispositivo")
    numero_serie: str = Field(..., min_length=5, description="Número de serie")
    estado: ESTADO_dispositivo = "disponible"

class CrearUsuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=3, description="Nombre usuario")
    departamento: str = Field(..., min_length=1, description="Departamento del usuario")
    correo: EmailStr

class CrearAsignacion(BaseModel):
    id: int = Field(..., gt=0)
    usuario_id: int = Field(..., gt=0)
    dispositivo_id: int = Field(..., gt=0)

@app.post("/v1/usuarios/", tags=["HTTP CRUD"], status_code=status.HTTP_201_CREATED)
async def agregar_usuarios(usuario: CrearUsuario):
    if any(usr["id"] == usuario.id for usr in usuarios):
        raise HTTPException(status_code=400, detail="El id ya existe")

    nuevo = usuario.model_dump()
    usuarios.append(nuevo)
    return {"mensaje": "Usuario creado", "datos": nuevo}

@app.post("/v1/dispositivos/", tags=["HTTP CRUD"], status_code=status.HTTP_201_CREATED)
async def agregar_dispositivos(dispositivo: CrearDispositivo):
    if any(disp["id"] == dispositivo.id for disp in dispositivos):
        raise HTTPException(status_code=400, detail="El id del dispositivo ya existe")

    nuevo = dispositivo.model_dump()
    dispositivos.append(nuevo)
    return {"mensaje": "Dispositivo creado", "datos": nuevo}

@app.get("/v1/usuarios/", tags=["HTTP CRUD"])
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}

@app.get("/v1/dispositivos/", tags=["HTTP CRUD"])
async def leer_dispositivos():
    return {"total": len(dispositivos), "dispositivos": dispositivos}

@app.get("/v1/dispositivos/{dispositivo_id}", tags=["HTTP CRUD"])
async def dispositivo_por_id(dispositivo_id: int):
    for dp in dispositivos:
        if dp["id"] == dispositivo_id:
            return dp
    raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

@app.post("/v1/asignaciones/", tags=["Asignaciones"], status_code=status.HTTP_201_CREATED)
async def registrar_asignacion(asignacion: CrearAsignacion):
    dispositivo = dispositivo_por_id_pres(asignacion.dispositivo_id)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    if dispositivo.get("estado") == "asignado":
        raise HTTPException(status_code=409, detail="El dispositivo ya está prestado")
    if any(a["id"] == asignacion.id for a in asignaciones):
        raise HTTPException(status_code=400, detail="El id de asignación ya existe")
    if not any(u["id"] == asignacion.usuario_id for u in usuarios):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    nuevo = asignacion.model_dump()
    nuevo["activo"] = True
    asignaciones.append(nuevo)

    for dp in dispositivos:
        if dp["id"] == asignacion.dispositivo_id:
            dp["estado"] = "asignado"
            break

    return {"mensaje": "Asignación registrada", "datos": nuevo}

@app.put("/v1/prestamos/{asignacion_id}/devolver", tags=["Préstamos"])
async def marcar_dispositivo_devuelto(asignacion_id: int):
    idx, asignacion = asignacion_por_id(asignacion_id)

    if asignacion is None:
        raise HTTPException(status_code=404, detail="El registro de préstamo no existe")
    if not asignacion.get("activo", True):
        raise HTTPException(status_code=409, detail="El préstamo ya fue devuelto")

    asignacion["activo"] = False
    asignaciones[idx] = asignacion

    for dp in dispositivos:
        if dp["id"] == asignacion["dispositivo_id"]:
            dp["estado"] = "disponible"
            break

    return {"mensaje": "Dispositivo desasignado", "prestamo_id": asignacion_id}

@app.delete("/v1/usuarios/{usuario_id}", tags=["HTTP CRUD"])
async def eliminar_usuario(usuario_id: int):
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuario_eliminado = usuarios.pop(i)
            return {
                "mensaje": "Usuario eliminado",
                "usuario": usuario_eliminado
            }

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.delete("/v1/dispositivos/{dispositivo_id}", tags=["HTTP CRUD"])
async def eliminar_dispositivo(dispositivo_id: int):
    for i, dp in enumerate(dispositivos):
        if dp["id"] == dispositivo_id:
            if dp["estado"] == "asignado":
                raise HTTPException(status_code=409, detail="No se puede eliminar un dispositivo asignado")

            dispositivo_eliminado = dispositivos.pop(i)
            return {
                "mensaje": "Dispositivo eliminado",
                "dispositivo": dispositivo_eliminado
            }

    raise HTTPException(status_code=404, detail="Dispositivo no encontrado")



# docker build -t api-dispositivos .
#docker run -d -p 5000:5000 --name api-fastapi api-dispositivos