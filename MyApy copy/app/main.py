from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel, Field

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token", auto_error=True)


SECRET_KEY = "mi-clave"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

usuarios = [
    {"id": 1, "nombre": "Fany", "edad": 21},
    {"id": 2, "nombre": "Ali", "edad": 21},
    {"id": 3, "nombre": "Dulce", "edad": 21},
]

def _hash_password(password: str) -> str:
    """Hashea una contraseña con bcrypt (devuelve string para guardar)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


usuarios_auth = {
    "admin": {
        "username": "admin",
        "hashed_password": _hash_password("secret123"),
    },
    "demo": {
        "username": "demo",
        "hashed_password": _hash_password("demo123"),
    },
}


def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Comprueba si la contraseña en texto plano coincide con el hash almacenado."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def obtener_usuario_auth(username: str) -> Optional[dict]:
    """Busca un usuario de autenticación por nombre de usuario."""
    return usuarios_auth.get(username)


def autenticar_usuario(username: str, password: str) -> Optional[dict]:
    """Si el usuario existe y la contraseña es correcta, devuelve el usuario; si no, None."""
    user = obtener_usuario_auth(username)
    if user is None:
        return None
    if not verificar_password(password, user["hashed_password"]):
        return None
    return user


def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
   
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> str:
 
    credential_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credential_error
    except JWTError:
        raise credential_error
    if obtener_usuario_auth(username) is None:
        raise credential_error
    return username


class CrearUsuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=3, max_length=50, example="Juanita")
    edad: int = Field(..., ge=1, le=123, description="Edad valida entre 1 y 123")


class PatchUsuario(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=50, example="Juanita")
    edad: Optional[int] = Field(None, ge=1, le=123, description="Edad valida entre 1 y 123")


@app.post("/v1/token", tags=["Autenticación"])
async def login_para_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible: recibe username y password en form-data.
    Si son correctos, devuelve un JWT con expiración de 30 minutos.
    """
    user = autenticar_usuario(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


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
async def actualizar_usuario_completo(
    usuario_id: int,
    usuario_actualizado: CrearUsuario,
    usuario_actual: str = Depends(obtener_usuario_actual),
):
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
async def eliminar_usuario(
    usuario_id: int,
    usuario_actual: str = Depends(obtener_usuario_actual),
):
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuario_eliminado = usuarios.pop(i)
            return {"mensaje": "Usuario eliminado", "usuario": usuario_eliminado}

    raise HTTPException(status_code=404, detail="Usuario no encontrado")

