from fastapi import status, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
#*************************
# Seguridad HTTP Basic
#*************************
seguridad = HTTPBasic()
def verificar_peticion(credenciales: HTTPBasicCredentials = Depends(seguridad)):
    usuario_correcto = secrets.compare_digest(credenciales.username, "admin")
    contrasena_correcta = secrets.compare_digest(credenciales.password, "admin123")
    if not (usuario_correcto and contrasena_correcta):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Credenciales inválidas"
        )
    return credenciales.username

